#!/bin/bash

# update the master bran


git diff HEAD~1 HEAD | curl -X POST -H "Content-Type: text/plain" --data-binary @- "$DOCUBUDDY_URL"