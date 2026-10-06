import { App } from "@modelcontextprotocol/ext-apps";

const serverTime = document.getElementById("server-time");
const refreshButton = document.getElementById("refresh-btn");

const app = new App({
  name: "Server Clock",
  version: "1.0.0",
});

function showResult(result) {
  const text = result.content
    ?.find((block) => block.type === "text")
    ?.text ?? "표시할 결과가 없습니다.";

  if (result.isError) {
    serverTime.textContent = `조회 실패: ${text}`;
    return;
  }

  const time = result.structuredContent?.result
    ?? text.split(/\r?\n/).find((line) => line.trim());

  serverTime.textContent = String(time ?? "시간이 없습니다.");
}

// 최초 결과를 놓치지 않도록 connect 전에 등록합니다.
app.ontoolresult = showResult;

refreshButton.addEventListener("click", async () => {
  refreshButton.disabled = true;
  serverTime.textContent = "조회 중입니다.";

  try {
    const result = await app.callServerTool({
      name: "get_server_time",
      arguments: {},
    });
    showResult(result);
  } catch (error) {
    serverTime.textContent = `호출 실패: ${String(error)}`;
  } finally {
    refreshButton.disabled = false;
  }
});

const faqInput = document.getElementById("faq-query");
const faqButton = document.getElementById("faq-btn");
const faqResponse = document.getElementById("faq-response");

faqButton.addEventListener("click", async () => {
  const query = faqInput.value;
  faqButton.disabled = true;
  faqResponse.textContent = "조회 중입니다.";

  try {
    const result = await app.callServerTool({
      name: "get_faq",
      arguments: { query },
    });

    const text = result.content
      ?.find((block) => block.type === "text")
      ?.text ?? "표시할 결과가 없습니다.";

    faqResponse.textContent = result.isError
      ? `조회 실패: ${text}`
      : String(result.structuredContent?.result ?? text);
  } catch (error) {
    faqResponse.textContent = `호출 실패: ${String(error)}`;
  } finally {
    faqButton.disabled = false;
  }
});

app.connect()
  .then(() => {
    refreshButton.disabled = false;
    faqButton.disabled = false;
  })
  .catch((error) => {
    serverTime.textContent = `Host 연결 실패: ${String(error)}`;
  });