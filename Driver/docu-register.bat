rmdir /S /Q .githooks
git submodule add -f -b master https://github.com/utkarsh-jha/docubuddy.git .githooks
git config core.hooksPath .githooks/Driver
git add .githooks
git commit -m "Added docubuddy submodule and configured hooks"