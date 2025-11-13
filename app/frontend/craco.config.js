// Load configuration from environment or config file
const path = require("path");

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === "true",
};

module.exports = {
  webpack: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
    configure: (webpackConfig, { env, paths }) => {
      // Production optimizations
      if (env === "production") {
        // Optimize bundle size with better chunk splitting
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          runtimeChunk: "single",
          splitChunks: {
            chunks: "all",
            cacheGroups: {
              // Separate vendor libraries into their own bundle
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name: "vendors",
                priority: 10,
                reuseExistingChunk: true,
              },
              // Separate Radix UI components
              radix: {
                test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
                name: "radix-ui",
                priority: 20,
                reuseExistingChunk: true,
              },
              // Separate React and DOM
              react: {
                test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
                name: "react-vendors",
                priority: 30,
                reuseExistingChunk: true,
              },
              // Common modules used by multiple chunks
              common: {
                minChunks: 2,
                priority: 5,
                reuseExistingChunk: true,
              },
            },
          },
        };
      }

      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter((plugin) => {
          return !(plugin.constructor.name === "HotModuleReplacementPlugin");
        });

        // Disable watch mode
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      } else {
        // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            "**/node_modules/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/coverage/**",
            "**/public/**",
          ],
        };
      }

      return webpackConfig;
    },
  },
  style: {
    postcss: {
      plugins: [
        require("tailwindcss"),
        require("autoprefixer"),
      ],
    },
  },
};
