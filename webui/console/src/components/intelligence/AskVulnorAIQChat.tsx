import { useEffect, useRef, useState } from "react";
import { Bot, SendHorizonal, ShieldQuestion } from "lucide-react";
import type { ChatMessage as ChatMessageType, Finding } from "@/types";
import { mockAssistantReply, starterPrompts } from "@/data/mock";
import { Button } from "@/components/ui/button";
import { ChatMessage } from "./ChatMessage";

let idCounter = 0;
const nextId = () => `m-${++idCounter}`;

export function AskVulnorAIQChat({ finding }: { finding: Finding }) {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Reset the conversation when the analyst switches findings.
  useEffect(() => {
    setMessages([
      {
        id: nextId(),
        role: "assistant",
        content: `I can help you understand and validate "${finding.title}". Ask how to test the fix, whether it risks regressions, or how to enforce it in CI/CD.`,
      },
    ]);
  }, [finding.id, finding.title]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    const userMsg: ChatMessageType = { id: nextId(), role: "user", content: trimmed };
    const pending: ChatMessageType = { id: nextId(), role: "assistant", content: "", pending: true };
    setMessages((prev) => [...prev, userMsg, pending]);
    setInput("");
    setBusy(true);

    // TODO(api): replace mocked reply with POST /api/assistant/chat once available.
    window.setTimeout(() => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pending.id
            ? { ...m, pending: false, content: mockAssistantReply(trimmed, finding) }
            : m,
        ),
      );
      setBusy(false);
    }, 750);
  };

  return (
    <div className="flex h-full flex-col">
      <div
        ref={scrollRef}
        className="flex-1 space-y-3 overflow-y-auto scrollbar-thin p-3"
      >
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}

        {messages.length <= 1 && (
          <div className="pt-1">
            <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
              <ShieldQuestion className="size-3.5" />
              Try asking
            </p>
            <div className="flex flex-col gap-1.5">
              {starterPrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="rounded-md border border-border bg-card px-2.5 py-1.5 text-left text-xs font-medium text-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="border-t border-border p-3"
      >
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(input);
              }
            }}
            rows={1}
            placeholder="Ask VulnorAIQ about this finding…"
            aria-label="Ask VulnorAIQ"
            className="max-h-28 min-h-[38px] flex-1 resize-none rounded-md border border-border bg-canvas px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          <Button type="submit" variant="primary" size="icon" disabled={busy || !input.trim()} aria-label="Send message">
            <SendHorizonal className="size-4" />
          </Button>
        </div>
        <p className="mt-2 flex items-center gap-1.5 text-[10.5px] leading-snug text-muted-foreground">
          <Bot className="size-3 shrink-0" />
          AI recommendations are advisory and require human review before applying to production.
        </p>
      </form>
    </div>
  );
}
