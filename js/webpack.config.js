const HtmlWebPackPlugin = require("html-webpack-plugin");
const path = require("path");

const CONFIG = {
  mode: "development",

  entry: {
    app: "./app.js",
  },

  output: {
    path: path.join(__dirname, "/dist"),
    filename: "bundle.js",
  },

  module: {
    rules: [
      {
        test: /\.js$/,
        loader: "babel-loader",
        exclude: [/node_modules/],
        options: {
          presets: ["@babel/preset-react"],
        },
      },
    ],
  },
  devServer: {
    port: 9000,
    open: false,
  },
  plugins: [
    new HtmlWebPackPlugin({
      hash: true,
      filename: "index.html",
      template: "./index.html",
    }),
  ],
};
module.exports = CONFIG;
