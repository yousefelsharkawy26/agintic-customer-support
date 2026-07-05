/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  transpilePackages: [
    'shared-types',
    '@nextui-org/react',
    '@nextui-org/theme',
    '@nextui-org/system',
    '@nextui-org/shared-utils',
  ],
};

module.exports = nextConfig;
