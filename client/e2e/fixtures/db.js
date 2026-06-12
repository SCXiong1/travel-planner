import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATE_PATH = path.join(__dirname, "travel.db.template");
const DB_PATH = path.resolve(__dirname, "../../../data/travel.db");

export function setupDatabase() {
  fs.copyFileSync(TEMPLATE_PATH, DB_PATH);
}

export function teardownDatabase() {
  fs.copyFileSync(TEMPLATE_PATH, DB_PATH);
}
