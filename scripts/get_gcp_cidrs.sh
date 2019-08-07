# Pulls the CIDRs for GCP so that we can whitelist the range the GitLab CI runners
while read -r CIDR_RECORD; do
       dig @8.8.8.8 \
           +short TXT "$CIDR_RECORD" | \
               grep -Pow '(\d+\.){3}\d+\/\d+';
   done < <(
       dig @8.8.8.8 \
           +short TXT _cloud-netblocks.googleusercontent.com | \
               grep -Pow '\_cloud.[^\ ]*.com'
   )
