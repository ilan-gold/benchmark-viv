To deploy, you need to download Terraform v0.11:

```bash
brew install terraform@0.11
```

The terraform file spins up two AWS instances - an http1 server and an http2 server.

To run the terraform configuration, you need to store the states somewhere:

```bash
 aws s3 mb s3://viv-benchmark --region us-east-1
```

Then when you initialize terraform, you provide that bucket name:

```bash
terraform init -upgrade -backend-config="bucket=viv-benchmark" -backend-config="region=us-east-1"
```

Next you can ininitialize the site configuration

```bash
terraform workspace new viv-benchmark
```

And finally, you can spin up (or update) resources:

```bash
terraform apply
```

Terraform automatically starts the HTTP1 and HTTP2 servers, the locations of which should be accessible in the terraform state files.  Use the IP address for benchmarking as we only need to use a self-signing certificate for SSL (instead of a real one).

