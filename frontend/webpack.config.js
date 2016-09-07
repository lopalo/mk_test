var webpack = require("webpack");


var config = {
    entry: "./index",
    output: {
        path: __dirname + "/../public/js",
        filename: "bundle.js"
    },
    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "babel",
                query: {
                    presets: ["es2015", "react"]
                }
            }
        ]
    },
    babel: {
        plugins: [
            "transform-object-rest-spread"
        ]
    },
    devtool: "eval-source-map",
};

module.exports = config;
