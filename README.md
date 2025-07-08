# 🚌 Otobüs Bilet Sistemi

**Hazırlayanlar:**  
Mehmet Şiyar Salman, Sühan Mustafa Kırdağ, Barış Toper, Onur Kocaman  
**Üniversite:** İstanbul Esenyurt Üniversitesi  
**Bölüm:** Yönetim Bilişim Sistemleri – 2. Sınıf  
**Ders:** Veritabanı Yönetim Sistemleri (VTYS) – Bahar Dönemi Projesi  

---

## 📌 Proje Hakkında

Bu proje, kullanıcıların çevrim içi olarak otobüs bileti satın almasını sağlar. Satın alınan bilet:
- QR kod olarak ekranda gösterilir  
- Aynı zamanda **PDF** olarak indirilebilir  
- Kullanıcı hesabı açılabilir ve giriş yapılabilir  
- Kullanıcı, **bilet geçmişini** görebilir  

---

## ⚙️ Kullanılan Teknolojiler

### 🔹 Backend:
- Python  
- Flask  
- SQLite

### 🔹 Frontend:
- HTML  
- CSS  
- JavaScript

---

## ⚠️ Bilinen Hatalar

- QR kod oluşturulduktan sonra tekrar bilet alınırsa, **önceki QR kodu hala ekranda kalmaktadır.**  
- Bu sorun, büyük ihtimalle **localStorage** ve kullanılan **QR kütüphanesinden** kaynaklanmaktadır.  
- Sorunu çözmek için “Bilet Bilgilerini Sil” butonuna basılması önerilir.  

---

## 🛠️ Kurulum

1. Bu projeyi GitHub’dan klonlayın:
