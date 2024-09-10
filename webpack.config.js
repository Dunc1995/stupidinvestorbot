const path = require('path');

module.exports = {
    entry: './web/src/app.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'web', 'static')
    },
    module: {
        rules: [
            {
                test: /\.(?:js|mjs|cjs)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', { targets: "defaults" }]
                        ]
                    }
                }
            },
            {
                test: /\.js$/,
                include: path.resolve(__dirname, 'web', 'src'),
                loader: 'babel-loader',
            },
        ],
    },
};