# SPEC sản phẩm: Chatbot Kuter - Giải pháp hỗ trợ học tập và vận hành VinAI Thực chiến

## 1. Bằng chứng (Evidence)

Nỗi đau của người dùng (học viên và ứng viên) được quan sát và ghi nhận trực tiếp từ thực tế vận hành lớp học:

### Trải nghiệm trực tiếp (Self-use)
Khi thành viên nhóm trải nghiệm chatbot hiện tại (**Trợ lý Kute**), bot gặp lỗi không thể giải đáp các thắc mắc về quy trình vận hành linh hoạt.
* **Chi tiết quan sát:** Thành viên Duy Bảo hỏi cách xử lý khi muốn đổi nhóm đã được ghép:
  * *Học viên hỏi:* "@Trợ lý Kute Dạ cho em hỏi là em ở team 062 nhưng vì một số lí do cá nhân nên muốn đổi lại team đã ghép thì có cách nào giải quyết không ạ"
  * *Bot phản hồi:* "@Mod Mình chưa đủ chắc chắn để trả lời chính xác câu hỏi này nên đã nhờ đội ngũ hỗ trợ giúp bạn nhé! 🙏"
* **Ảnh chụp màn hình:**
  ![Trải nghiệm trực tiếp của thành viên nhóm](evidence/evidence_1.png)
* **Những chỗ thấy vướng (Friction points):**
  * **Thiếu hụt tri thức động:** Câu hỏi về việc đổi nhóm này thực chất đã từng được hỏi và có câu trả lời/hướng dẫn cụ thể từ admin/mentor trên Discord trước đó. Tuy nhiên, Trợ lý Kute hoàn toàn không có kiến thức này do chỉ được trang bị thông tin tĩnh từ Handbook PDF.
  * Bot lập tức đầu hàng và tag Mod khi gặp câu hỏi thực tế phát sinh, buộc học viên phải đợi ban tổ chức phản hồi thủ công, làm chậm tiến độ làm việc nhóm.

### Nguồn từ bên ngoài nhóm
Quan sát hành vi của các học viên khác trong lớp khi tương tác với chatbot hiện tại.
* **Chi tiết quan sát:** Học viên Lê Bá Chiến hỏi xin tài liệu học tập:
  * *Học viên hỏi:* "@Trợ lý Kute cho tao xin slide day 4"
  * *Bot phản hồi:* "@Mod Mình chưa đủ chắc chắn để trả lời chính xác câu hỏi này nên đã nhờ đội ngũ hỗ trợ giúp bạn nhé! 🙏"
* **Ảnh chụp màn hình:**
  ![Tương tác của học viên ngoài nhóm](evidence/evidence_2.png)
* **Những chỗ thấy vướng (Friction points):**
  * **Thiếu đồng bộ tài nguyên:** Link slide các buổi học (trong đó có slide Day 4) đã được admin chia sẻ và trả lời rõ ràng trên Discord. Tuy nhiên, chatbot cũ vẫn không thể tự truy cập hay trả lời được do không cập nhật dữ liệu Q&A Discord.
  * Gây quá tải tin nhắn rác trên kênh chung và tốn công sức hỗ trợ thủ công của admin/mentor cho các câu hỏi lặp đi lặp lại đã có lời giải.

---

## 2. Lát cắt để build (Build slice)

Nhóm phát triển **Kuter** dưới dạng một giải pháp tích hợp hai thành phần chính:
1. **Discord Bot (Prototype chính):** Chatbot hoạt động trực tiếp trên server Discord của lớp học để hỗ trợ học viên và mentor giải đáp thắc mắc.
2. **Web Interface (VinUni Clone):** Bản sao trang landing page của chương trình VinAI Thực chiến tích hợp widget bong bóng chat chứa iframe để minh họa cách nhúng Kuter vào website phục vụ ứng viên mới.

Quyết định cốt lõi của AI: Khi nhận câu hỏi, hệ thống sẽ tự động so khớp ngữ nghĩa với cơ sở tri thức động (Rule-base). Nếu không khớp, AI RAG sẽ tự động truy xuất tài liệu Handbook PDF. Nếu câu hỏi nằm ngoài phạm vi tài liệu, bot kích hoạt cơ chế Fallback và cho phép Mentor cập nhật trực tiếp tri thức mới.

---

## 3. AI Product Canvas

| Ô | Nội dung chi tiết |
|---|---|
| **Value** — Giá trị | - **Đối tượng:** Học viên, ứng viên và ban tổ chức chương trình VinAI Thực chiến.<br>- **Nỗi đau:** Trợ lý Kute cũ chỉ trả lời từ Handbook tĩnh, hoàn toàn "mù" thông tin Q&A động và lỗi kỹ thuật phát sinh thực tế trên Discord.<br>- **AI giải quyết:** Tích hợp RAG từ Handbook PDF kết hợp với Rule-base động (mentor-driven) được cập nhật thời gian thực qua tính năng Reply trên Discord. |
| **Trust** — Niềm tin | - **Nhận diện sai:** Gắn nhãn nguồn rõ ràng (ví dụ: tiền tố `**[Rule-base]**` hoặc trích dẫn trang tài liệu từ PDF) để người dùng biết cơ sở câu trả lời.<br>- **Xử lý sai:** Khi AI không tìm thấy thông tin, bot gửi tin nhắn thông báo lỗi/chưa có dữ liệu rõ ràng, tránh bịa đặt thông tin (hallucination). Đồng thời mở cổng cho Mentor phản hồi trực tiếp để ghi đè hoặc bổ sung tri thức. |
| **Feasibility** — Tính khả thi | - **Dữ liệu:** File Handbook PDF chính thức (`20K_AI_handbook_ver2.pdf`) và file JSON cơ sở dữ liệu tri thức động (`rulebase.json`).<br>- **Công nghệ:** Model `gemini-2.5-flash` và `gemini-embedding-001` qua LangChain, cơ sở dữ liệu vector FAISS cục bộ.<br>- **Rủi ro lớn nhất:** AI bịa đặt quy định hành chính sai lệch.<br>- **Ngưỡng dừng:** Sử dụng prompt strict constraint. Nếu RAG chain trả về kết quả không có trong tài liệu (phát hiện cụm từ *"I don't know based on the provided document"*), bot lập tức dừng và chuyển sang luồng Fallback. |
| **Tín hiệu học** | Khi Mentor thực hiện **Reply** trực tiếp vào tin nhắn chờ trên Discord, cặp Câu hỏi - Câu trả lời mới sẽ được lưu vào file `rulebase.json` và tự động cập nhật cache embedding của bot tức thì để cải thiện tri thức cho các lần hỏi tiếp theo. |

---

## 4. Tăng năng lực hay tự động hóa (Augment vs Automate)

* **Conditional Automation (Tự động hóa có điều kiện):**
  * *Tự động hóa hoàn toàn (Automate):* Đối với các câu hỏi hành chính đã có quy định rõ ràng trong Handbook PDF (Kuter tự động dùng RAG trích xuất và trả lời kèm số trang cụ thể).
  * *Tăng năng lực con người (Augment):* Đối với các câu hỏi phát sinh thực tế hoặc lỗi kỹ thuật. Kuter chỉ trả lời nếu đã được Mentor dạy trước đó (qua Rule-base động). Nếu chưa có, bot đóng vai trò ghi nhận lỗi (`new_issue.json`) và hỗ trợ Mentor trong việc thu thập và biên soạn câu trả lời mới một cách nhanh chóng nhất.
  * *Lý do chọn:* Đảm bảo độ chính xác tuyệt đối đối với các quy chế hành chính của chương trình, tránh việc AI tự suy diễn các chính sách hoặc giải pháp kỹ thuật chưa được kiểm chứng, đồng thời tối ưu quy trình cập nhật tri thức của ban vận hành.

---

## 5. Bốn đường đi của trải nghiệm (Four paths)

| Đường đi | Kịch bản trải nghiệm thực tế trên Discord |
|---|---|
| **Đường thuận** | Học viên hỏi câu hỏi hành chính (ví dụ: điều kiện nhận chứng chỉ) -> Bot dùng RAG tìm trong Handbook PDF -> Trả lời chính xác kèm số trang trích dẫn. |
| **Khi AI không chắc** | Học viên hỏi câu hỏi ngoài tài liệu -> RAG trả về *"I don't know..."* -> Bot gửi câu trả lời Fallback thông báo chưa có thông tin, đồng thời ghi log vào `new_issue.json` ở trạng thái pending. |
| **Khi AI sai** | RAG đưa ra câu trả lời không chính xác hoặc học viên nhận thấy câu trả lời thiếu cập nhật -> Mentor/Admin phát hiện và muốn điều chỉnh tri thức cho bot. |
| **Khi người dùng sửa** | Mentor dùng tính năng **Reply** của Discord trả lời tin nhắn pending của học viên -> Bot tự động bắt sự kiện, lưu cặp Q&A chuẩn vào `rulebase.json` và cập nhật cache embedding. Lần sau khi học viên khác hỏi câu tương tự, bot nhận diện ngữ nghĩa (Cosine Similarity >= 0.85) và trả lời ngay với nhãn `**[Rule-base]**`. |

---

## 6. Những kiểu lỗi đáng lo nhất

1. **Hallucination thông tin quy chế:**
   * *Khi nào xảy ra:* Khi LLM cố suy diễn thông tin nằm ngoài văn bản Handbook PDF.
   * *Cách xử lý:* Sử dụng strict system prompt ép LLM trả về cụm từ quy định *"I don't know based on the provided document."* nếu không tìm thấy context khớp trong vector database.
2. **So khớp nhầm câu hỏi trong Rule-base (False Positive):**
   * *Khi nào xảy ra:* Khi học viên đặt câu hỏi có từ khóa giống nhưng ý nghĩa khác với câu hỏi cũ đã được Mentor duyệt trong Rule-base.
   * *Cách xử lý:* Cấu hình ngưỡng tương đồng Cosine Similarity cao (ngưỡng `0.85`) khi tìm kiếm trên cache embedding của `rulebase.json` để đảm bảo độ tin cậy.

---

## 7. Kế hoạch kiểm thử và bằng chứng demo

* **Kịch bản kiểm thử Happy Path (RAG Handbook):**
  * *Đầu vào:* "/ask Điều kiện nhận chứng chỉ tốt nghiệp của chương trình là gì?"
  * *Kỳ vọng:* Kuter trả lời rõ ràng kèm trích dẫn số trang cụ thể từ Handbook PDF.
* **Kịch bản kiểm thử Fallback Path (Ngoài phạm vi):**
  * *Đầu vào:* "/ask Làm sao để đổi chủ đề nhóm đã chọn?" (Giả định câu hỏi này chưa có trong rulebase).
  * *Kỳ vọng:* Bot phản hồi thông báo xin lỗi chưa có thông tin và hướng dẫn Mentor reply. File `new_issue.json` được cập nhật thêm câu hỏi này.
* **Kịch bản kiểm thử Dynamic Update (Mentor dạy học):**
  * *Đầu vào:* Mentor dùng tính năng **Reply** vào tin nhắn chờ trên của học viên với nội dung: "Em hãy dùng lệnh /ticket trên Discord để báo ban tổ chức hỗ trợ đổi chủ đề nhé."
  * *Kỳ vọng:* Bot gửi phản hồi xác nhận *"Đã lưu vào Rule-base!"*. File `rulebase.json` ghi nhận cặp câu hỏi và câu trả lời này. Khi học viên hỏi lại "/ask em muốn đổi chủ đề nhóm chọn thế nào", bot tự động tìm thấy trong Rule-base và trả lời chính xác với tiền tố `**[Rule-base]**`.

---

## 8. Phân công

*(Chưa phân công cụ thể - Sẽ cập nhật sau)*
