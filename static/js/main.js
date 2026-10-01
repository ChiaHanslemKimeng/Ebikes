/**
 * VoltRide Ultra-Modern E-Commerce Frontend Scripts
 * Handles AJAX Cart, Wishlist, Quick-View Modal, Search Autocomplete, and Toasts.
 */

// Helper to retrieve CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Toast Notification Dispatcher
function showVoltToast(message, type = 'success') {
    const toastContainer = document.getElementById('voltToastContainer');
    if (!toastContainer) return;

    const iconMap = {
        'success': 'fa-check-circle text-success',
        'info': 'fa-info-circle text-info',
        'warning': 'fa-exclamation-triangle text-warning',
        'error': 'fa-times-circle text-danger',
        'danger': 'fa-times-circle text-danger'
    };
    const icon = iconMap[type] || 'fa-bell text-primary';

    const toastEl = document.createElement('div');
    toastEl.className = 'toast toast-voltride align-items-center show mb-2';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex p-3 align-items-center">
            <i class="fas ${icon} fa-lg me-3"></i>
            <div class="toast-body flex-grow-1 p-0 fw-semibold text-white">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white ms-3" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
    bsToast.show();

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. AJAX Add to Cart
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-ajax-add-cart');
        if (!btn) return;
        e.preventDefault();

        const productId = btn.getAttribute('data-product-id');
        let quantity = 1;
        const qtyInput = document.getElementById(`qtyInput_${productId}`);
        if (qtyInput) {
            quantity = parseInt(qtyInput.value) || 1;
        }

        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';

        const formData = new FormData();
        formData.append('quantity', quantity);

        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
            if (data.status === 'success') {
                showVoltToast(data.message, 'success');
                // Update cart count badges
                document.querySelectorAll('.cart-count-badge').forEach(el => {
                    el.textContent = data.cart_count;
                });
            } else {
                showVoltToast(data.message || 'Error adding item to cart.', 'error');
            }
        })
        .catch(err => {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
            showVoltToast('Could not add product to cart. Please try again.', 'error');
        });
    });

    // 2. AJAX Wishlist Toggle
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-wishlist-toggle');
        if (!btn) return;
        e.preventDefault();

        const productId = btn.getAttribute('data-product-id');

        fetch(`/wishlist/toggle/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => {
            if (res.status === 401 || res.redirected || res.url.includes('/account/login/')) {
                window.location.href = `/account/login/?next=${encodeURIComponent(window.location.pathname)}`;
                return null;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            if (data.status === 'success') {
                showVoltToast(data.message, 'info');
                // Toggle active style
                if (data.action === 'added') {
                    btn.classList.add('active');
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    }
                } else {
                    btn.classList.remove('active');
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                }
                // Update wishlist count badges
                document.querySelectorAll('.wishlist-count-badge').forEach(el => {
                    el.textContent = data.wishlist_count;
                });
            }
        })
        .catch(() => {
            showVoltToast('Please sign in to save items to your wishlist.', 'warning');
        });
    });

    // 3. Quick View Modal Trigger
    const quickViewModal = document.getElementById('quickViewModal');
    if (quickViewModal) {
        const bsModal = new bootstrap.Modal(quickViewModal);
        document.body.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-quick-view');
            if (!btn) return;
            e.preventDefault();

            const slug = btn.getAttribute('data-slug');
            fetch(`/product/${slug}/quick-view/`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(p => {
                document.getElementById('qvTitle').textContent = p.name;
                document.getElementById('qvCategory').textContent = p.category;
                document.getElementById('qvSku').textContent = `SKU: ${p.sku}`;
                document.getElementById('qvDescription').textContent = p.short_description;
                document.getElementById('qvImage').src = p.image_url;
                document.getElementById('qvImage').alt = p.name;
                document.getElementById('qvPrice').textContent = `$${p.current_price}`;
                
                const oldPriceEl = document.getElementById('qvPriceOld');
                if (p.is_on_sale) {
                    oldPriceEl.textContent = `$${p.price}`;
                    oldPriceEl.classList.remove('d-none');
                } else {
                    oldPriceEl.classList.add('d-none');
                }

                // Specs list
                const specsList = document.getElementById('qvSpecsList');
                specsList.innerHTML = '';
                if (p.motor_power) specsList.innerHTML += `<li><strong>Motor:</strong> ${p.motor_power}</li>`;
                if (p.battery_capacity) specsList.innerHTML += `<li><strong>Battery:</strong> ${p.battery_capacity}</li>`;
                if (p.range) specsList.innerHTML += `<li><strong>Range:</strong> ${p.range}</li>`;
                if (p.maximum_speed) specsList.innerHTML += `<li><strong>Speed:</strong> ${p.maximum_speed}</li>`;
                if (p.warranty) specsList.innerHTML += `<li><strong>Warranty:</strong> ${p.warranty}</li>`;

                // Add to cart button in modal
                const addCartBtn = document.getElementById('qvAddToCartBtn');
                addCartBtn.setAttribute('data-product-id', p.id);

                // View Details Link
                document.getElementById('qvDetailLink').href = p.url;

                bsModal.show();
            })
            .catch(() => {
                showVoltToast('Could not load quick preview.', 'error');
            });
        });
    }

    // 4. Site-wide Search Autocomplete
    const searchInputs = document.querySelectorAll('.site-search-input');
    searchInputs.forEach(input => {
        const resultsContainer = input.parentElement.querySelector('.search-autocomplete-results');
        if (!resultsContainer) return;

        let debounceTimer;
        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const query = input.value.trim();
            if (query.length < 2) {
                resultsContainer.classList.add('d-none');
                resultsContainer.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/search/autocomplete/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.results && data.results.length > 0) {
                        let html = '<div class="list-group list-group-flush shadow-lg rounded-3 border">';
                        data.results.forEach(item => {
                            html += `
                                <a href="${item.url}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3">
                                    <div>
                                        <div class="fw-bold text-dark small">${item.title}</div>
                                        <span class="badge bg-light text-muted border">${item.category}</span>
                                    </div>
                                    <span class="text-primary fw-bold small">$${item.price}</span>
                                </a>
                            `;
                        });
                        html += `
                            <a href="/search/?q=${encodeURIComponent(query)}" class="list-group-item list-group-item-action text-center py-2 text-primary small fw-bold">
                                See all matching results <i class="fas fa-arrow-right ms-1"></i>
                            </a>
                        </div>`;
                        resultsContainer.innerHTML = html;
                        resultsContainer.classList.remove('d-none');
                    } else {
                        resultsContainer.classList.add('d-none');
                    }
                });
            }, 250);
        });

        // Hide results on outside click
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.classList.add('d-none');
            }
        });
    });

    // 5. AJAX Newsletter Signup
    const newsletterForms = document.querySelectorAll('.newsletter-form-ajax');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Subscribing...';

            const formData = new FormData(form);
            fetch('/newsletter/subscribe/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                if (data.status === 'success') {
                    showVoltToast(data.message, 'success');
                    form.reset();
                } else {
                    showVoltToast(data.message || 'Error subscribing.', 'error');
                }
            })
            .catch(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                showVoltToast('Could not subscribe. Please try again.', 'error');
            });
        });
    });
});
