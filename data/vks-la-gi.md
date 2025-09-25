# VKS là gì?

VKS (VNGCloud Kubernetes Service) là một dịch vụ được quản lý trên VNGCloud giúp bạn đơn giản hóa quá trình triển khai và quản lý các ứng dụng dựa trên container. Kubernetes là một nền tảng mã nguồn mở được phát triển bởi Google, được sử dụng rộng rãi để quản lý và triển khai các ứng dụng container trên môi trường phân tán.

<figure><img src="../.gitbook/assets/vks_la_gi.png" alt=""><figcaption></figcaption></figure>



***

## Những điểm nổi bật của VKS <a href="#whatisvks-nhungdiemnoibatcuavks" id="whatisvks-nhungdiemnoibatcuavks"></a>

* **Quản lý Control Plane hoàn toàn tự động (Fully Managed control plane):** VKS sẽ giải phóng bạn khỏi gánh nặng quản lý Control Plane của Kubernetes, giúp bạn tập trung vào việc phát triển ứng dụng.
* **Hỗ trợ các phiên bản Kubernetes mới nhất:** VKS luôn cập nhật những phiên bản Kubernetes mới nhất (minor version từ 1.28, 1.29. 1.30) để đảm bảo bạn luôn tận dụng được những tính năng tiên tiến nhất.
* **Kubernetes Networking:** VKS tích hợp Calico CNI, Cilium Overlay CNI và Cilium VPC Native Routing CNI, mang lại tính hiệu quả và bảo mật cao.
* **Upgrade seamlessly:** VKS hỗ trợ nâng cấp giữa các phiên bản Kubernetes một cách dễ dàng và nhanh chóng, giúp bạn luôn cập nhật những cải tiến mới nhất.
* **Scaling & Healing Automatically:** VKS tự động mở rộng Node group khi cần thiết và tự động sửa lỗi khi node gặp vấn đề, giúp bạn tiết kiệm thời gian và công sức quản lý.
* **Giảm chi phí và nâng cao độ tin cậy:** VKS triển khai Control Plane của Kubernetes ở chế độ sẵn sàng cao và hoàn toàn miễn phí, giúp bạn tiết kiệm chi phí và nâng cao độ tin cậy cho hệ thống.
* **Tích hợp Blockstore Native (Container Storage Interface - CSI):** VKS cho phép bạn quản lý Blockstore thông qua YAML của Kubernetes, cung cấp lưu trữ bền vững cho container và hỗ trợ các tính năng quan trọng như thay đổi kích thước, thay đổi IOPS và snapshot volume.
* **Tích hợp Load Balancer (Network Load Balancer, Application Load Balancer) thông qua vLB Native Integration Driver:** VKS cung cấp khả năng quản lý NLB/ALB thông qua YAML của Kubernetes, giúp bạn dễ dàng expose Service trong Kubernetes ra bên ngoài.
* **Nâng cao bảo mật:** VKS cho phép bạn tạo Private Node Group với chỉ Private IP và kiểm soát quyền truy cập vào cluster thông qua tính năng Whitelist IP, đảm bảo an toàn cho hệ thống của bạn.

**Ngoài ra, VKS còn có các ưu điểm sau:**

* Dễ sử dụng: VKS cung cấp giao diện đơn giản và dễ sử dụng.
* Chi phí hợp lý: VKS cung cấp mức giá cạnh tranh cho các dịch vụ của mình.

***

### **Region** <a href="#farm" id="farm"></a>

Hiện tại, trên VKS, chúng tôi đang cung cấp cho bạn 2 cơ sở hạ tầng riêng biệt được đặt tại Hà Nội và Hồ Chí Minh. Bạn có thể lựa chọn sử dụng VKS trên mỗi region tùy thuộc vào vị trí và nhu cầu thực tế của bạn. Đối với 2 farm HCM03, HAN01, các thông số cụ thể cho mỗi region được chúng tôi cung cấp như sau:

<table><thead><tr><th width="140">Farm</th><th>Domain</th></tr></thead><tbody><tr><td>HCM03</td><td><a href="https://vks.console.vngcloud.vn/overview">https://vks.console.vngcloud.vn</a></td></tr><tr><td>HAN01</td><td><a href="https://vks-han-1.console.vngcloud.vn/overview">https://vks-han-1.console.vngcloud.vn</a></td></tr></tbody></table>
