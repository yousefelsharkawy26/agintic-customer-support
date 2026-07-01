/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  transpilePackages: ['shared-types'],
};

module.exports = nextConfig;
