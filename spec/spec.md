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
  * **Thiếu đồng bộ tài nguyên:** Link slide các buổi học (trong đó có slide Day 4) đã được hỏi trên Discord. Tuy nhiên, chatbot cũ vẫn không thể tự truy cập hay trả lời được do không cập nhật dữ liệu Q&A Discord.
  * Gây quá tải tin nhắn trên kênh chung.

---

## 2. Lát cắt để build (Build slice)

Cho học viên và ứng viên VinAI Thực chiến đang cần câu trả lời hành chính hoặc tài nguyên học tập, **Kuter** sẽ dùng AI RAG kết hợp đa nguồn để:
1. **Automate** trả lời chính xác các câu hỏi FAQ hành chính dựa trên Handbook PDF (kèm trích dẫn số trang).
2. **Augment** câu trả lời cho các câu hỏi vận hành và kỹ thuật bằng cách trích xuất, tổng hợp từ lịch sử hỏi đáp (Discord Q&A) giữa admin/mentor và học viên để đưa ra gợi ý giải pháp nháp nhanh chóng.
3. **Fallback** an toàn bằng nút "Báo cáo Mentor" và disclaimer rõ ràng khi độ tin cậy thấp hoặc câu hỏi ngoài phạm vi dữ liệu.

---

## 3. AI Product Canvas

| Ô | Nội dung chi tiết |
|---|---|
| **Value** — Giá trị | - **Đối tượng:** Học viên và ứng viên VinAI Thực chiến.<br>- **Nỗi đau:** Trợ lý Kute cũ chỉ trả lời từ Handbook tĩnh, không cập nhật được Q&A vận hành và tài nguyên trên Discord.<br>- **AI giải quyết:** RAG tích hợp Handbook tĩnh và Q&A Discord động giúp học viên tự giải quyết vấn đề ngay lập tức. |
| **Trust** — Niềm tin | - **Nhận diện sai:** Người dùng dễ dàng nhận diện nhờ disclaimer rõ ràng gắn kèm mọi câu trả lời kỹ thuật/vận hành từ Discord.<br>- **Xử lý sai:** Cung cấp nút "Báo cáo Mentor" ngay dưới câu trả lời và hệ thống bình chọn Thumbs Up/Down để hoàn tác và chuyển tiếp lên Mentor/Admin thực tế. |
| **Feasibility** — Tính khả thi | - **Dữ liệu cần có:** Handbook PDF chính thức và lịch sử Q&A trên Discord đã được làm sạch.<br>- **Rủi ro lớn nhất:** AI hallucinate ra giải pháp kỹ thuật/thủ tục sai lệch gây bối rối cho học viên.<br>- **Ngưỡng dừng:** Nếu độ tin cậy của câu trả lời < 75%, bot tự động chuyển luồng sang tag Mentor hỗ trợ trực tiếp. |
| **Tín hiệu học** | Khi học viên nhấn Thumbs Down hoặc "Báo cáo Mentor", câu hỏi và câu trả lời lỗi sẽ được tự động log lại vào cơ sở dữ liệu hiệu chỉnh để ban tổ chức kiểm duyệt, cập nhật dữ liệu huấn luyện hoặc tinh chỉnh prompt. |

---

## 4. Tăng năng lực hay tự động hóa (Augment vs Automate)

* **Conditional Automation (Tự động hóa có điều kiện):**
  * *Tự động hóa hoàn toàn (Automate):* Đối với các câu hỏi hành chính rõ ràng có sẵn nguồn trong Handbook (như điều kiện tham gia, lịch trình chung).
  * *Tăng năng lực con người (Augment):* Đối với các câu hỏi vận hành phức tạp hoặc lỗi kỹ thuật. Kuter chỉ tổng hợp lịch sử Discord làm gợi ý nháp để học viên tham khảo tự sửa lỗi, không tự ý đưa ra quyết định thay cho con người.
  * *Lý do chọn:* Giảm thiểu rủi ro AI đưa ra hướng dẫn kỹ thuật sai lệch làm học viên nản lòng, đồng thời giảm tải tối đa cho Mentor khỏi những câu hỏi lặp đi lặp lại.

---

## 5. Bốn đường đi của trải nghiệm (Four paths)

| Đường đi | Kịch bản trải nghiệm |
|---|---|
| **Đường thuận** | Học viên hỏi "Điều kiện tham gia lớp là gì?" -> Kuter truy xuất Handbook và trả lời chính xác kèm số trang trích dẫn. |
| **Khi AI không chắc** | Học viên hỏi câu hỏi kỹ thuật phức tạp -> Kuter đưa ra giải pháp nháp dựa trên lịch sử Discord kèm disclaimer cảnh báo và nút "Báo cáo Mentor". |
| **Khi AI sai** | Bot đưa ra câu trả lời không đúng -> Học viên bấm Thumbs Down hoặc nút "Báo cáo Mentor" để hủy câu trả lời và kích hoạt ticket hỗ trợ cho Mentor thực tế. |
| **Khi người dùng sửa** | Học viên bấm báo cáo hoặc phản hồi -> Hệ thống log lại câu hỏi, câu trả lời sai và câu trả lời sửa đổi để cải tiến tri thức cho bot sau này. |

---

## 6. Những kiểu lỗi đáng lo nhất

1. **Hallucination thông tin hành chính/quy định:**
   * *Khi nào xảy ra:* Khi quy định thay đổi đột ngột hoặc dữ liệu Handbook bị chồng chéo.
   * *Hậu quả:* Học viên nhận thông tin sai về deadline hoặc cách tính điểm, dẫn đến mất điểm hoặc vi phạm nội quy.
   * *Cách xử lý:* Luôn đính kèm citation số trang gốc của Handbook và cập nhật cơ sở dữ liệu ngay khi có thông báo mới.
2. **Gợi ý code/lỗi kỹ thuật sai:**
   * *Khi nào xảy ra:* Khi lỗi của học viên quá mới hoặc lịch sử Discord chứa thông tin nhiễu.
   * *Hậu quả:* Học viên chạy code lỗi nghiêm trọng hơn, gây ức chế.
   * *Cách xử lý:* Gắn disclaimer nổi bật và cung cấp nút báo cáo Mentor tức thì.

---

## 7. Kế hoạch kiểm thử và bằng chứng demo

* **Kịch bản kiểm thử Happy Path:**
  * *Đầu vào:* "Xin thông tin về điều kiện nhận chứng chỉ và số trang Handbook nói về điều này."
  * *Kỳ vọng:* Kuter trả lời rõ ràng kèm trích dẫn số trang chính xác.
* **Kịch bản kiểm thử Low-Confidence / Fallback Path:**
  * *Đầu vào:* "Lỗi đổi nhóm sau khi đã ghép cặp giải quyết thế nào?" hoặc "Lấy slide bài giảng Day 4 ở đâu?"
  * *Kỳ vọng:* Kuter trích xuất câu trả lời đã có trên Discord, hiển thị cảnh báo thông tin tham khảo và hiển thị nút "Báo cáo Mentor".

---

## 8. Phân công

*(Chưa phân công cụ thể - Sẽ cập nhật sau)*
