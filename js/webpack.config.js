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
        // Transpile ES6 to ES5 with babel
        // Remove if your app does not use JSX or you don't need to support old browsers
        test: /\.js$/,
        loader: "babel-loader",
        exclude: [/node_modules/],
        options: {
          presets: ["@babel/preset-react"],
        },
      },
    ],
  },
  plugins: [
    new HtmlWebPackPlugin({
      hash: true,
      filename: "index.html", // target html
      template: "./index.html", // source html
    }),
  ],
};

// This line enables bundling against src in this repo rather than installed module
module.exports = CONFIG;
