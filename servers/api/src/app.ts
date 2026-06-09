import Fastify, { type FastifyInstance } from 'fastify';

/** 构建 Fastify 应用：当前仅健康检查，无业务逻辑。 */
export function buildApp(): FastifyInstance {
  const app = Fastify({ logger: true });

  app.get('/health', async () => {
    return { status: 'ok' };
  });

  return app;
}
