// Sayfa geçişi için efekt
document.body.style.opacity = 0;
window.addEventListener("load", () => {
    document.body.style.transition = "opacity 1s";
    document.body.style.opacity = 1;
});


window.addEventListener("scroll", () => {
    const navbar = document.querySelector("nav");
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = "#333";
            navbar.style.boxShadow = "0 2px 10px rgba(0,0,0,0.3)";
        } else {
            navbar.style.backgroundColor = "transparent";
            navbar.style.boxShadow = "none";
        }
    }
});

// Scroll ile reveal animasyonu
const revealElements = document.querySelectorAll(".reveal");
const revealOnScroll = () => {
    revealElements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            el.style.opacity = 1;
            el.style.transform = "translateY(0)";
        }
    });
};


function getCurrentUserId() {
   
    return localStorage.getItem('userId') || 1; 
}


function createBiletCard(bilet) {
    return `
        <div class="bilet-karti reveal">
            <h3>${bilet.nereden} → ${bilet.nereye}</h3>
            <p><strong>Tarih/Saat:</strong> ${bilet.tarih} | ${bilet.saat}</p>
            <p><strong>Koltuk:</strong> ${bilet.koltuk_no}</p>
            <p><strong>Fiyat:</strong> ${bilet.fiyat} TL</p>
            <p class="durum ${bilet.durum === 'Onaylandı' ? 'onayli' : 'beklemede'}">
                ${bilet.durum}
            </p>
        </div>
    `;
}


function loadBiletGecmisi() {
    const container = document.getElementById('bilet-listesi');
    if (!container) return;

    container.innerHTML = '<p class="yukleniyor">Yükleniyor...</p>';

    fetch(`/api/bilet-gecmisi?kullanici_id=${getCurrentUserId()}`)
        .then(response => {
            if (!response.ok) throw new Error('HTTP hatası: ' + response.status);
            return response.json();
        })
        .then(data => {
            container.innerHTML = data.biletler?.length > 0 
                ? data.biletler.map(createBiletCard).join('') 
                : '<p class="bos-liste">Henüz biletiniz bulunmamaktadır.</p>';
            
            
            setTimeout(revealOnScroll, 50);
        })
        .catch(error => {
            console.error('Hata:', error);
            container.innerHTML = `
                <p class="hata">
                    Biletler yüklenirken hata oluştu.<br>
                    <small>${error.message}</small>
                </p>
            `;
        });
}


document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('bilet-gecmisi.html')) {
        loadBiletGecmisi();
    }
});


window.addEventListener("scroll", () => {
    revealOnScroll();
    
});
window.addEventListener("load", revealOnScroll);