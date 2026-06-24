import {
  Bot,
  Boxes,
  Database,
  FileCode2,
  FolderGit2,
  MessageSquareCode,
  type LucideIcon,
} from "lucide-react";
import type { AssetType } from "@/types";

export const assetTypeMeta: Record<
  AssetType,
  { label: string; icon: LucideIcon }
> = {
  repository: { label: "Repository", icon: FolderGit2 },
  file: { label: "Source File", icon: FileCode2 },
  container_image: { label: "Container Image", icon: Boxes },
  ai_agent: { label: "AI Agent", icon: Bot },
  llm_app: { label: "LLM Application", icon: MessageSquareCode },
  rag_store: { label: "RAG / Vector Store", icon: Database },
};
