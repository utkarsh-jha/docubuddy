@echo off
setlocal

git checkout master 
git pull origin master
set API_ENDPOINT=https://localhost:5000/api
set DOCUBUDDY_URL=%API_ENDPOINT%
if "%DOCUBUDDY_URL%"=="" (
    echo Environment variable API_ENDPOINT is not set
    exit /b 1
)

git diff HEAD~1 HEAD | curl -X POST -H "Content-Type: text/plain" --data-binary @- "%URL%" | git apply -

endlocal