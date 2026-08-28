/**
 * Real-Time SSE Stream Consumer for RAG Chat API
 * Handles token-by-token streaming with smooth markdown rendering and source citations.
 */

async function streamChatMessage({
  endpoint = "/rag/api/chat/",
  storeId,
  query,
  systemPrompt = "",
  sessionId = "",
  onToken,
  onComplete,
  onError,
}) {
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
      },
      body: JSON.stringify({
        store_id: storeId,
        query: query,
        system_prompt: systemPrompt,
        session_id: sessionId,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let accumulatedText = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // Keep partial line in buffer

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data: ")) continue;

        const jsonStr = trimmed.replace(/^data:\s*/, "");
        try {
          const payload = JSON.parse(jsonStr);

          if (payload.token) {
            accumulatedText += payload.token;
            if (typeof onToken === "function") {
              onToken(payload.token, accumulatedText);
            }
          }

          if (payload.done) {
            if (typeof onComplete === "function") {
              onComplete({
                fullText: accumulatedText,
                sources: payload.sources || [],
                citations: payload.citations || [],
                responseTime: payload.response_time || "",
                responseTimeSeconds: payload.response_time_seconds || 0,
              });
            }
            return;
          }
        } catch (parseErr) {
          console.warn("Failed to parse SSE line:", trimmed, parseErr);
        }
      }
    }

    // If stream closed without explicit done signal
    if (typeof onComplete === "function") {
      onComplete({
        fullText: accumulatedText,
        sources: [],
        citations: [],
        responseTime: "",
      });
    }
  } catch (err) {
    console.error("SSE Chat Streaming Error:", err);
    if (typeof onError === "function") {
      onError(err);
    }
  }
}

if (typeof window !== "undefined") {
  window.streamChatMessage = streamChatMessage;
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = { streamChatMessage };
}
