"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const child_process_1 = require("child_process");
const app = (0, express_1.default)();
const port = 8081;
const allowedOrigins = ["http://localhost:3000", "http://localhost:3001"];
const options = {
    origin: allowedOrigins,
};
app.use((0, cors_1.default)(options));
// app.use(cors());
app.use(express_1.default.json());
let output = "";
app.get("/chat", (req, res) => {
    // res.send("Typescript + Node.js + Express Server");
    const net = (0, child_process_1.spawn)("python", ["script.py"]);
    output = "";
    //파이썬 파일 수행 결과를 받아온다
    net.stdout.on("data", function (data) {
        output += data.toString();
        res.send(output);
    });
});
app
    .listen(port, () => {
    console.log(`[server]: Server is running at <http://localhost>:${port}`);
})
    .on("error", (error) => {
    throw new Error(error.message);
});
