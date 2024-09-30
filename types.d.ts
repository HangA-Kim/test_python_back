declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: "development" | "production" | "test";
      OPENAI_API_KEY;
    }
  }
}

export {};
