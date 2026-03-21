// ═══════════════════════════════════════════════════════════════════════
// state_store.ts
// Atomic JSON file store with schema validation and crash-safe writes
// SINGLE-PROCESS SAFE ONLY (uses in-process spin-lock)
// ═══════════════════════════════════════════════════════════════════════

import * as fs from "fs";
import * as path from "path";
import { PersistentStore, JobRecord, CURRENT_SCHEMA_VERSION } from "./types.js";

export class FileStore {
  private readonly filePath: string;
  private readonly backupDir: string;
  private locked = false;

  constructor(filePath: string) {
    this.filePath = filePath;
    this.backupDir = path.join(path.dirname(filePath), "store_backups");

    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    if (!fs.existsSync(this.backupDir)) {
      fs.mkdirSync(this.backupDir, { recursive: true });
    }

    this.ensureValidStore();
  }

  private ensureValidStore(): void {
    if (!fs.existsSync(this.filePath)) {
      this.write({
        version: 0,
        createdAt: new Date().toISOString(),
        schemaVersion: CURRENT_SCHEMA_VERSION,
        jobs: {},
      });
      return;
    }

    try {
      const raw = fs.readFileSync(this.filePath, "utf-8");
      const parsed: unknown = JSON.parse(raw);
      if (!this.validateSchema(parsed)) {
        this.backupAndReinit();
      }
    } catch (err) {
      console.warn(`[FileStore] corrupted or unreadable: ${this.filePath}`, err);
      this.backupAndReinit();
    }
  }

  private validateSchema(data: unknown): data is PersistentStore {
    if (!data || typeof data !== "object") {
      return false;
    }
    const d = data as Partial<PersistentStore>;
    if (typeof d.version !== "number") {
      return false;
    }
    if (typeof d.schemaVersion !== "number") {
      return false;
    }
    if (d.schemaVersion !== CURRENT_SCHEMA_VERSION) {
      return false;
    }
    if (!d.createdAt || typeof d.createdAt !== "string") {
      return false;
    }
    if (!d.jobs || typeof d.jobs !== "object") {
      return false;
    }

    for (const [, v] of Object.entries(d.jobs)) {
      if (!v || typeof v !== "object") {
        return false;
      }
      const j = v as Partial<JobRecord>;
      if (typeof j.id !== "string") {
        return false;
      }
      if (typeof j.workflowId !== "string") {
        return false;
      }
      if (typeof j.status !== "string") {
        return false;
      }
      if (!Array.isArray(j.steps)) {
        return false;
      }
    }

    return true;
  }

  private backupAndReinit(): void {
    const timestamp = Date.now();
    const backupPath = path.join(this.backupDir, `store.BACKUP.${timestamp}.json`);

    try {
      fs.renameSync(this.filePath, backupPath);
      console.warn(`[FileStore] backed up corrupt file to: ${backupPath}`);
    } catch {
      try {
        fs.unlinkSync(this.filePath);
      } catch {
        /* ignore */
      }
    }

    this.write({
      version: 0,
      createdAt: new Date().toISOString(),
      schemaVersion: CURRENT_SCHEMA_VERSION,
      jobs: {},
    });
  }

  read(): PersistentStore {
    const raw = fs.readFileSync(this.filePath, "utf-8");
    const parsed = JSON.parse(raw);
    if (!this.validateSchema(parsed)) {
      throw new Error(`[FileStore] schema validation failed on read`);
    }
    return JSON.parse(fs.readFileSync(this.filePath, "utf-8"));
  }

  private write(store: PersistentStore): void {
    store.version++;
    const tmpFile = this.filePath + ".tmp";
    fs.writeFileSync(tmpFile, JSON.stringify(store, null, 2), "utf-8");
    fs.renameSync(tmpFile, this.filePath);
  }

  async tx<T>(fn: (store: PersistentStore) => T): Promise<T> {
    while (this.locked) {
      await new Promise<void>((r) => setTimeout(r, 5));
    }
    this.locked = true;
    try {
      const store = this.read();
      const result = fn(store);
      this.write(store);
      return result;
    } finally {
      this.locked = false;
    }
  }

  getJob(jobId: string): JobRecord | undefined {
    return this.read().jobs[jobId];
  }

  listJobs(): JobRecord[] {
    return Object.values(this.read().jobs);
  }
}
