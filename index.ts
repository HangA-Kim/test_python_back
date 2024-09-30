import express, { Express, Request, Response } from "express";
// import cors from "cors";
import { spawn } from "child_process";
import path from "path";

// console.log(path.join(__dirname)); // 루트 경로. 배포때와 개발때의 경로가 달라서

const isDevelopment = (): boolean => {
  // console.log("NODE_ENV>", process.env.NODE_ENV);
  // npm install cross-env --save-dev
  // "dev": "cross-env NODE_ENV=development nodemon --exec ts-node ./index.ts"
  return process.env.NODE_ENV === "development";
};

const app: Express = express();
const port = 8080;
// const allowedOrigins = ["http://localhost:3000", "http://localhost:3001"];
// const options: cors.CorsOptions = {
//   origin: allowedOrigins,
// };
// app.use(cors(options));
// app.use(cors());
app.use(express.json());
// app.use(bodyParser.json())

app.get("/", (request, response) => {
  response.send("hello World http test");
});

app.post("/chat", (req: Request, res: Response) => {
  // res.send("Typescript + Node.js + Express Server");

  const reqQuestion = req.body.question;

  const pythonExePath = isDevelopment()
    ? path.join(__dirname, "chat", "Scripts", "python.exe")
    : path.join(__dirname, "chat", "bin", "python3");

  // const pythonExePath = path.join(__dirname, "chat", "bin", "python3");
  const defaultSrcPath = path.join(__dirname, "chat");

  const net = spawn(pythonExePath, [
    path.join(defaultSrcPath, "bizchat.py"),
    reqQuestion,
    path.join(defaultSrcPath, "data"),
  ]);

  let output = "";
  //파이썬 파일 수행 결과를 받아온다
  net.stdout.on("data", function (data) {
    output += data.toString();
    // res.send(data.toString());
  });

  net.on("close", (code) => {
    if (code === 0) {
      // res.send(output);
      res.status(200).json({ answer: output });
    } else {
      res.status(500).send("Something went wrong");
    }
  });

  net.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });
});

app
  .listen(port, () => {
    console.log(`[server]: Server is running at <http://localhost>:${port}`);
  })
  .on("error", (error) => {
    throw new Error(error.message);
  });
