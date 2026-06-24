import { MessagesSquare, Radar } from "lucide-react";
import type { Finding } from "@/types";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CveMetadataCard } from "./CveMetadataCard";
import { CweDescriptionCard } from "./CweDescriptionCard";
import { IntelligenceMappingCard } from "./IntelligenceMappingCard";
import { AskVulnorAIQChat } from "./AskVulnorAIQChat";

export function IntelligencePanel({ finding }: { finding: Finding }) {
  return (
    <Tabs defaultValue="intel" className="flex h-full flex-col">
      <div className="border-b border-border p-3">
        <TabsList className="w-full">
          <TabsTrigger value="intel">
            <Radar className="size-3.5" />
            Intelligence
          </TabsTrigger>
          <TabsTrigger value="chat">
            <MessagesSquare className="size-3.5" />
            Ask VulnorAIQ
          </TabsTrigger>
        </TabsList>
      </div>

      <TabsContent
        value="intel"
        className="flex-1 space-y-3 overflow-y-auto scrollbar-thin p-3 data-[state=inactive]:hidden"
      >
        <CveMetadataCard cve={finding.cve} />
        <CweDescriptionCard cwe={finding.cwe} />
        <IntelligenceMappingCard mapping={finding.intelligence} />
      </TabsContent>

      <TabsContent
        value="chat"
        className="flex-1 overflow-hidden data-[state=inactive]:hidden"
      >
        <AskVulnorAIQChat finding={finding} />
      </TabsContent>
    </Tabs>
  );
}
