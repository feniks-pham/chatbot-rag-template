# Sử dụng VKS với Terraform

### Terraform là gì?

Terraform là một cơ sở hạ tầng nguồn mở dưới dạng công cụ mã cho phép người dùng quản lý cơ sở hạ tầng của họ một cách dễ dàng và hiệu quả trên các nền tảng đám mây khác nhau, chẳng hạn như VNG Cloud, AWS, Google Cloud và Azure. Máy chủ Terraform đề cập đến phiên bản của công cụ Terraform đang chạy trên một máy chủ hoặc máy cụ thể. Đây là nơi mã cơ sở hạ tầng được viết và thực thi, cho phép người dùng tạo, sửa đổi và hủy tài nguyên trên nền tảng đám mây.

Bản thân Terraform không có giao diện người dùng đồ họa, thay vào đó người dùng tương tác với nó bằng giao diện dòng lệnh. Terraform yêu cầu tài khoản và khóa của nhà cung cấp đám mây được định cấu hình cùng với tệp cấu hình Terraform để thực thi cơ sở hạ tầng dưới dạng mã. Ngoài ra, Terraform có thể hoạt động trong môi trường nhóm nơi nhiều người dùng có thể cộng tác trên cùng một cơ sở mã cơ sở hạ tầng, khiến nó trở thành một công cụ mạnh mẽ và linh hoạt để quản lý cơ sở hạ tầng đám mây.

***

### Các bước thực hiện <a href="#quanlyvcontainervoiterraform-dequanlyvcontainervoiterraform-bancanlamcacbuocsauday" id="quanlyvcontainervoiterraform-dequanlyvcontainervoiterraform-bancanlamcacbuocsauday"></a>

Để khởi tạo một Cluster Kubernetes bằng Terraform, bạn cần thực hiện các bước sau:

1. **Truy cập IAM Portal** tại [đây](https://iam.console.vngcloud.vn/), thực hiện tạo Service Account với quyền hạn **VKS Full Access**. Cụ thể, tại trang IAM, bạn có thể:
   * Chọn "**Create a Service Account**", điền tên cho Service Account và nhấn **Next Step** để gắn quyền cho Service Account.
   * Tìm và chọn **Policy:** **VKSFullAccess** sau đó nhấn "**Create a Service Account**" để tạo Service Account, **Policy: VKSFullAccess** do VNG Cloud tạo ra, bạn không thể xóa các policy này.
   * Sau khi tạo thành công bạn cần phải lưu lại **Client\_ID** và **Secret\_Key** của Service Account để thực hiện bước tiếp theo.
2. **Truy cập VKS Portal** tại [đây](https://vks.console.vngcloud.vn/overview)**, thực hiện Activate** dịch vụ VKS ở tab **Overview.** Hãy chờ đợi tới khi chúng tôi khởi tạo thành công tài khoản VKS của bạn.
3. **Cài đặt Terraform:**
   * Tải xuống và cài đặt Terraform cho hệ điều hành của bạn từ [https://developer.hashicorp.com/terraform/install](https://developer.hashicorp.com/terraform/install).
4. **Khởi tạo cấu hình Terraform:**
   * Tạo tệp `variable.tf` và khai báo thông tin Service Account trong file này.
   * Tạo tệp `main.tf` và định nghĩa các tài nguyên Kubernetes Cluster mà bạn muốn tạo.

Ví dụ:

* Tệp `variable.tf:`bạn cần thay thế Client ID và Client Secret đã khởi tạo ở bước 1 ở file này.

```
variable "client_id" {
  type = string
  default = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
variable "client_secret" {
  type = string
  default = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

* Tệp `main.tf` khi tạo Cluster/ Node Group trên **Region HCM:**

```
terraform {
  required_providers {
    vngcloud = {
      source  = "vngcloud/vngcloud"
      version = "1.3.3"
    }
  }
}
provider "vngcloud" {
  token_url        = "https://iamapis.vngcloud.vn/accounts-api/v2/auth/token"
  client_id        = var.client_id
  client_secret    = var.client_secret
  vserver_base_url = "https://hcm-3.api.vngcloud.vn/vserver/vserver-gateway"
  vlb_base_url     = "https://hcm-3.api.vngcloud.vn/vserver/vlb-gateway"
  vks_base_url     = "https://vks.api.vngcloud.vn"
}

resource "vngcloud_vks_cluster" "primary" {
  name      = "cluster-hcm"
  description = "Cluster create via terraform"
  version = "v1.29.13-vks.1740045600"
  enable_private_cluster = true
  network_type = "CILIUM_NATIVE_ROUTING"
  cidr      = "172.16.0.0/16"
  vpc_id    = "net-dc27a89b-e7a8-46eb-bba1-9339fa6bd018"
  subnet_id = "sub-1191201a-4b47-46b8-8049-f18889ff5677"
  secondary_subnets = ["10.111.128.0/20","10.111.144.0/20"]
  node_netmask_size = 25
  enable_service_endpoint = true
  enabled_load_balancer_plugin = true
  enabled_block_store_csi_plugin = true
  lifecycle {
    create_before_destroy = true
  }
}

resource "vngcloud_vks_cluster_node_group" "primary" {
  cluster_id = vngcloud_vks_cluster.primary.id
  name = "nodegroup1"
  num_nodes = 3
  auto_scale_config {
    min_size = 0
    max_size = 5
  }
  upgrade_config {
    strategy = "SURGE"
    max_surge = 1
    max_unavailable = 0
  }
  image_id = "img-53bccbb6-7db5-42c1-bcc2-fef9fd1dccdc"
  flavor_id = "flav-305a67bf-1825-4e3f-bc72-d41afa160d93"
  subnet_id = "sub-1191201a-4b47-46b8-8049-f18889ff5677"
  secondary_subnets = ["10.111.160.0/20"]
  disk_size = 50
  disk_type = "vtype-2fc64a6c-38e3-4f08-93a5-18018cb3ab23"
  enable_private_nodes = true
  ssh_key_id= "ssh-7e899107-b5dd-4b91-9c82-5e20497cb00b"
  labels = {
    "test" = "terraform"
  }
  taint {
    key    = "key1"
    value  = "value1"
    effect = "PreferNoSchedule"
  }
  lifecycle {
    create_before_destroy = true
  }
}



```

* Tệp `main.tf` khi tạo Cluster/ Node Group trên **Region HAN:**

```
terraform {
  required_providers {
    vngcloud = {
      source  = "vngcloud/vngcloud"
      version = "1.3.3"
    }
  }
}
provider "vngcloud" {
  token_url        = "https://iamapis.vngcloud.vn/accounts-api/v2/auth/token"
  client_id        = var.client_id
  client_secret    = var.client_secret
  vserver_base_url = "https://han-1.api.vngcloud.vn/vserver/vserver-gateway"
  vlb_base_url     = "https://han-1.api.vngcloud.vn/vserver/vlb-gateway"
  vks_base_url     = "https://vks-han-1.api.vngcloud.vn"
}

resource "vngcloud_vks_cluster" "primary" {
  name      = "cluster-demo"
  description = "Cluster create via terraform"
  version = "v1.29.13-vks.1740045600"
  enable_private_cluster = true
  network_type = "CILIUM_NATIVE_ROUTING"
  cidr      = "172.16.0.0/16"
  vpc_id    = "net-0dc4cf1e-d961-4483-b848-62ed86fa69f1"
  subnet_id = "sub-a39ebafb-4231-4a86-b94e-f78fc6b8778d"
  secondary_subnets = ["192.168.200.0/24"]
  node_netmask_size = 25
  enable_service_endpoint = true
  enabled_load_balancer_plugin = true
  enabled_block_store_csi_plugin = true
  lifecycle {
    create_before_destroy = true
  }
}

resource "vngcloud_vks_cluster_node_group" "primary" {
  cluster_id = vngcloud_vks_cluster.primary.id
  name = "nodegroup1"
  num_nodes = 3
  auto_scale_config {
    min_size = 0
    max_size = 5
  }
  upgrade_config {
    strategy = "SURGE"
    max_surge = 1
    max_unavailable = 0
  }
  image_id = "img-331724e8-326f-4fd0-ac6e-f9bd127f976c"
  flavor_id = "flav-305a67bf-1825-4e3f-bc72-d41afa160d93"
  subnet_id = "sub-a39ebafb-4231-4a86-b94e-f78fc6b8778d"
  secondary_subnets = ["192.168.200.0/24"]
  disk_size = 50
  disk_type = "vtype-7a7a8610-34f5-11ee-be56-0242ac120002"
  enable_private_nodes = true
  ssh_key_id= "ssh-4e765839-4222-444b-bf09-83de37aa7121"
  labels = {
    "test" = "terraform"
  }
  taint {
    key    = "key1"
    value  = "value1"
    effect = "PreferNoSchedule"
  }
  lifecycle {
    create_before_destroy = true
  }
}

```

{% hint style="info" %}
**Chú ý:**

* Chúng tôi khuyên bạn nên tạo và quản lý các Cluster, Node Group dưới dạng resource riêng biệt, như trong ví dụ bên dưới. Điều này cho phép bạn thêm hoặc xóa các Node Group mà không cần tạo lại toàn bộ Cluster. Nếu bạn khai báo trực tiếp Node Group Default trong tài nguyên vngcloud\_vks\_cluster, bạn không thể xóa chúng mà không tạo lại chính Cluster đó.
*   Trong file main.tf, để khởi tạo một cluster với một node group thành công, bạn bắt buộc cần nhập thông tin của 4 field sau:

    ```
      vpc_id    = "net-xxxxxxxx-xxxx-xxxxx-xxxx-xxxxxxxxxxxx"
      subnet_id = "sub-xxxxxxxx-xxxx-xxxxx-xxxx-xxxxxxxxxxxx"
      ssh_key_id= "ssh-xxxxxxxx-xxxx-xxxxx-xxxx-xxxxxxxxxxxx"
    ```
* Để lấy image\_id, flavor\_id bạn mong muốn sử dụng, bạn có thể truy cập vào VKS Portal, chọn menu System Image và lấy ID mà bạn mong muốn.
{% endhint %}

### **Khởi chạy Terraform command** <a href="#quanlyvcontainervoiterraform-khoichayterraformcommand" id="quanlyvcontainervoiterraform-khoichayterraformcommand"></a>

* Sau khi hoàn tất các thông tin trên, thực hiện chạy lệnh bên dưới:

```
terraform init
```

* Sau đó, bạn để xem những thay đổi sẽ được áp dụng trên những resource mà terraform đang quản lý bạn có thể chạy:

```
terraform plan
```

* Cuối cùng bạn chọn chạy dòng lệnh:

```
terraform apply
```

* Chọn **YES** để thực hiện việc khởi tạo Cluster, Node Group thông qua Terraform
* Nếu bạn không còn nhu cầu sử dụng Cluster, bạn có thể xóa bằng lệnh:

```
terraform destroy
```

***

### **Kiểm tra Cluster vừa tạo trên giao diện VNG Cloud Portal** <a href="#quanlyvcontainervoiterraform-kiemtracontainervuataotrengiaodienvngcloudportal" id="quanlyvcontainervoiterraform-kiemtracontainervuataotrengiaodienvngcloudportal"></a>

Sau khi khởi tạo thành công Terraform, bạn có thể lên VKS Portal để xem thông tin Cluster vừa tạo.

Tham khảo thêm về cách sử dụng Terraform để làm việc với VKS tại [đây](https://registry.terraform.io/providers/vngcloud/vngcloud/latest/docs/resources/vks_cluster).

### **Một số lưu ý khi sử dụng VKS với Terraform:**

Khi sử dụng **Terraform** để khởi tạo **Cluster** và **Node Group** trên hệ thống VKS, nếu bạn thay đổi một trong các field sau, hệ thống sẽ tự động xóa Node Group/ Cluster và thực hiện khởi tạo lại Node Group/ Cluster theo thông số mới tương ứng. Việc xóa sẽ được thực hiện trước khi tạo Node Group/ Cluster mới.

* Đỗi với resource `vngcloud_vks_cluster`, các field khi bạn thay đổi hệ thống sẽ xóa Cluster và tạo lại bao gồm:
  * `name`&#x20;
  * `description`&#x20;
  * `enable_private_cluster`&#x20;
  * `network_type`&#x20;
  * `vpc_id`&#x20;
  * `subnet_id`&#x20;
  * `cidr`&#x20;
  * `enabled_load_balancer_plugin`&#x20;
  * `enabled_block_store_csi_plugin`&#x20;
  * `node_group`&#x20;
  * `secondary_subnets`&#x20;
  * `node_netmask_size`
* Đỗi với resource `vngcloud_vks_cluster_node_group`, các field khi bạn thay đổi hệ thống sẽ xóa Cluster và tạo lại bao gồm:
  * `cluster_id`&#x20;
  * `name`&#x20;
  * `flavor_id`&#x20;
  * `disk_size`&#x20;
  * `disk_type`&#x20;
  * `enable_private_nodes`&#x20;
  * `ssh_key_id`&#x20;
  * `secondary_subnets`&#x20;
  * `enabled_encryption_volume`&#x20;
  * `subnet_id`

Để chỉ định hệ thống tạo cluster/node group mới rồi mới thực hiện xóa cluster/ node group cũ, bạn có thể thêm tham số `lifecycle { create_before_destroy = true }`vào file main.tf của bạn. Cụ thể:

* Đỗi với resource `vngcloud_vks_cluster`

```
resource "vngcloud_vks_cluster" "example" {
  # ...
 
  lifecycle {
    create_before_destroy = true
  }
}
```

* Đỗi với resource `vngcloud_vks_cluster_node_group`

```
resource "vngcloud_vks_cluster_node_group" "example" {
  # ...
 
  lifecycle {
    create_before_destroy = true
  }
}
```

