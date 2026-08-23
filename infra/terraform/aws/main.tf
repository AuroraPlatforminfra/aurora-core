terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "aurora" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "aurora-vpc"
  }
}

resource "aws_subnet" "aurora" {
  count             = 3
  vpc_id            = aws_vpc.aurora.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "aurora-subnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "aurora" {
  vpc_id = aws_vpc.aurora.id

  tags = {
    Name = "aurora-igw"
  }
}

resource "aws_route_table" "aurora" {
  vpc_id = aws_vpc.aurora.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.aurora.id
  }

  tags = {
    Name = "aurora-rt"
  }
}

resource "aws_route_table_association" "aurora" {
  count          = 3
  subnet_id      = aws_subnet.aurora[count.index].id
  route_table_id = aws_route_table.aurora.id
}

resource "aws_security_group" "aurora_eks" {
  name        = "aurora-eks-sg"
  description = "Security group for Aurora EKS"
  vpc_id      = aws_vpc.aurora.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "aurora-eks-sg"
  }
}

resource "aws_security_group" "aurora_rds" {
  name        = "aurora-rds-sg"
  description = "Security group for Aurora RDS"
  vpc_id      = aws_vpc.aurora.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.aurora_eks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "aurora-rds-sg"
  }
}

resource "aws_db_subnet_group" "aurora" {
  name       = "aurora-db-subnet-group"
  subnet_ids = aws_subnet.aurora[*].id

  tags = {
    Name = "aurora-db-subnet-group"
  }
}

resource "aws_db_instance" "aurora" {
  identifier              = "aurora-db"
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  storage_type            = "gp3"
  storage_encrypted       = true
  multi_az                = false
  publicly_accessible     = false
  
  db_name                 = "aurora"
  username                = "aurora"
  password                = random_password.db_password.result
  
  db_subnet_group_name    = aws_db_subnet_group.aurora.name
  vpc_security_group_ids  = [aws_security_group.aurora_rds.id]
  
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"
  
  skip_final_snapshot = true

  tags = {
    Name = "aurora-db"
  }
}

resource "aws_iam_role" "eks_cluster" {
  name = "aurora-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_eks_cluster" "aurora" {
  name            = "aurora-core-cluster"
  role_arn        = aws_iam_role.eks_cluster.arn
  version         = "1.28"

  vpc_config {
    subnet_ids              = aws_subnet.aurora[*].id
    security_group_ids      = [aws_security_group.aurora_eks.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = {
    Name = "aurora-core-cluster"
  }
}

resource "aws_iam_role" "eks_node" {
  name = "aurora-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node.name
}

resource "aws_iam_role_policy_attachment" "eks_ssm_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.eks_node.name
}

resource "aws_eks_node_group" "aurora" {
  cluster_name    = aws_eks_cluster.aurora.name
  node_group_name = "aurora-nodes"
  node_role_arn   = aws_iam_role.eks_node.arn
  subnet_ids      = aws_subnet.aurora[*].id

  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 3
  }

  instance_types = ["t3.medium"]
  disk_size      = 100

  tags = {
    Name = "aurora-nodes"
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
  ]
}

resource "aws_ecr_repository" "aurora" {
  name                 = "aurora-core"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "aurora-core"
  }
}

resource "aws_ecr_lifecycle_policy" "aurora" {
  repository = aws_ecr_repository.aurora.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus     = "tagged"
        tagPrefixList = ["v"]
        countType     = "imageCountMoreThan"
        countNumber   = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

output "cluster_name" {
  value       = aws_eks_cluster.aurora.name
  description = "EKS cluster name"
}

output "cluster_endpoint" {
  value       = aws_eks_cluster.aurora.endpoint
  description = "EKS cluster endpoint"
}

output "cluster_version" {
  value       = aws_eks_cluster.aurora.version
  description = "EKS cluster version"
}

output "db_endpoint" {
  value       = aws_db_instance.aurora.endpoint
  description = "RDS instance endpoint"
}

output "db_name" {
  value       = aws_db_instance.aurora.db_name
  description = "Database name"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.aurora.repository_url
  description = "ECR repository URL"
}

output "vpc_id" {
  value       = aws_vpc.aurora.id
  description = "VPC ID"
}
