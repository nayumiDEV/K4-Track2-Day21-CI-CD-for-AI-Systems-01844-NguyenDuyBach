# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Nguyễn Duy Bách |
| MSSV | 01844 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/nayumiDEV/K4-Track2-Day21-CI-CD-for-AI-Systems-01844-NguyenDuyBach |
| Ngày nộp | 21/08/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 2 | 100 | 0.10 | 3 | 0.7109 | 0.8780 |
| 3 | 200 | 0.10 | 5 | 0.7149 | 0.8740 |
| 4 | 150 | 0.15 | 4 | 0.7182 | 0.8760 |

**Bộ siêu tham số đã chọn:** `n_estimators=150`, `learning_rate=0.15`, `max_depth=4`.

**Lý do:** Bộ tham số này đạt F1 cao nhất (0.7182) trên tập đánh giá. Lần chạy có accuracy cao nhất là lần 2 (0.8780), nhưng F1 lại thấp hơn lần 4 (0.7109 so với 0.7182). Sự lệch pha này cho thấy accuracy bị chi phối bởi lớp đa số, trong khi F1 phản ánh chính xác khả năng bắt đúng nhóm thu nhập cao. Khi `learning_rate` nhỏ (0.05) kết hợp ít cây (50), mô hình chưa học đủ sâu. Ngược lại, việc tăng lên 200 cây với độ sâu 5 làm tăng thời gian tính toán nhưng F1 lại giảm nhẹ so với mức 150 cây độ sâu 4 do bắt đầu xuất hiện hiện tượng khớp quá mức.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult bị mất cân bằng lớp rõ rệt với khoảng 75% mẫu thuộc nhóm thu nhập thấp (<= 50K) và chỉ 25% thuộc nhóm thu nhập cao (> 50K). Nếu một mô hình đơn giản chỉ dự đoán toàn bộ là "thu nhập thấp", nó vẫn đạt mức accuracy 75% dù không học được bất kỳ tri thức nào từ dữ liệu. Vì vậy, accuracy là một chỉ số gây hiểu nhầm lớn trong bài toán này.

F1 của lớp dương giải quyết vấn đề đó bằng cách kết hợp cả precision và recall dành riêng cho nhóm thu nhập cao, đo lường trực tiếp mức độ nhận diện chuẩn xác của lớp thiểu số. Chúng ta không dùng `average="weighted"` hay `average="macro"` vì các cách tính trung bình này vẫn bị kéo điểm bởi 75% dữ liệu của lớp đa số. Việc giữ nguyên binary F1 trên nhãn dương đảm bảo quality gate chỉ cho phép mô hình đi tiếp khi thực sự dự đoán tốt nhóm mục tiêu.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Pipeline trên GitHub Actions bị dừng ở bước train do lỗi module sqlite và mlflow. | Môi trường runner là máy ảo sạch, thiếu các gói phụ thuộc để tracking MLflow vào file db. | Bổ sung các thư viện cần thiết vào requirements.txt để runner cài đặt trước khi chạy script huấn luyện. |
| Dữ liệu mới cập nhật không tự động kích hoạt workflow trên GitHub. | Quên chạy lệnh thêm dữ liệu vào DVC hoặc push code lên Git trước khi push dữ liệu lên cloud storage. | Chạy dvc add cho file dữ liệu, thực hiện dvc push trước rồi mới commit file con trỏ .dvc và git push. |
| Kho lưu trữ Git bị phình to dung lượng khi lưu file mô hình và dữ liệu thô. | Chưa cấu hình loại trừ các file nhị phân lớn trong thư mục models và data. | Cập nhật file .gitignore để Git chỉ quản lý mã nguồn và file con trỏ .dvc. |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7182 | 0.8760 |
| Bước 3 (thêm `train_batch2`) | 0.7489 | 0.8860 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu từ `train_batch2`, chỉ số F1 tăng từ 0.7182 lên 0.7489 và accuracy tăng từ 0.8760 lên 0.8860. Vì tập dữ liệu mới có cùng phân phối với tập cũ nên sự cải thiện này chủ yếu đến từ việc mô hình có thêm các mẫu biên để phân định ranh giới quyết định rõ ràng hơn. Quan trọng nhất, toàn bộ pipeline CI/CD đã tự động kích hoạt từ commit dữ liệu và triển khai thành công mô hình mới lên server mà không cần bất kỳ thao tác thủ công nào.
