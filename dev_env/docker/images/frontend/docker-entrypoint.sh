#!/bin/sh

if [[ -d "node_modules" ]]; then
  rm -rf node_modules
fi

if [[ -d "static" ]]; then
  rm -rf static
fi

mkdir -p static

# Installs based on the package-lock.json.
#npm --max-old-space-size=2048 ci --prefer-offline --no-audit --progress=false
npm install -g npm@8.12.1

npm install --prefer-offline --no-audit --progress=false

echo "[ + ] Starting Webpack"
npm --max-old-space-size=2048 run dev