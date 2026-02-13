/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack config (boş bırakarak default kullanıyoruz)
  turbopack: {},

  // better-sqlite3 için webpack config
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals.push({
        'better-sqlite3': 'commonjs better-sqlite3'
      });
    }
    return config;
  },
};

module.exports = nextConfig;
