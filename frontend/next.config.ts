import createNextIntlPlugin from 'next-intl/plugin';
const withNextIntl = createNextIntlPlugin();

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ['37.151.21.4', 'localhost'],
};

export default withNextIntl(nextConfig);
