#!/bin/sh

if [[ -d "node_modules" ]]; then
  rm -rf node_modules
fi

if [[ -d "static" ]]; then
  rm -rf static
fi

mkdir -p static

npm i

echo "[ + ] Starting Webpack"
npm run dev