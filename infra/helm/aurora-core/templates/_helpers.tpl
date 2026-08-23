{{- define "aurora-core.fullname" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | trunc 63 }}
{{- end }}
