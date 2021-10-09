// const path = require('path');
// const glob = require('glob');
// const MiniCssExtractPlugin = require('mini-css-extract-plugin');
// const PurgecssPlugin = require('purgecss-webpack-plugin');
const LodashModuleReplacementPlugin = require('lodash-webpack-plugin');
const TerserPlugin = require("terser-webpack-plugin");
const dev = process.env.NODE_ENV !== 'production';

// const PATHS = {
//   src: path.join(__dirname, 'src')
// };
let config = {
  watchOptions: {
    poll: true,
    ignored: /node_modules/
  },
  devtool: dev ? 'eval-cheap-module-source-map' : false,
  plugins: [
    // new BundleAnalyzerPlugin(),
    //   new MiniCssExtractPlugin({
    //   filename: "[name].css",
    // }),
    // new PurgecssPlugin({
    //   paths: glob.sync(`${PATHS.src}/**/*`,  { nodir: true }),
    // }),
    new LodashModuleReplacementPlugin
  ],
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()],
    splitChunks: {
      cacheGroups: {
        styles: {
          name: 'styles',
          test: /\.css$/,
          chunks: 'all',
          enforce: true
        },
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    },
    runtimeChunk: {
      name: 'manifest'
    }
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {

          loader: 'babel-loader',
          options: {
            plugins: ['lodash'],
            presets: ['@babel/preset-env']
          }
        },
      },
      {
        test: /\.css$/,
        use: ["style-loader", 'css-loader'] //MiniCssExtractPlugin.loader
      },
      {
        test: /\.(jpg|jpeg|png|woff|woff2|eot|ttf|svg)$/,
        use: [{
          loader: 'url-loader',
          options: {
            limit: 50000
          }
        }],
      }
    ]
  }
}

if(dev){
  const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
  config.plugins.push(new BundleAnalyzerPlugin())
}

module.exports = config;
