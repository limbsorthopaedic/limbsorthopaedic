// WhatsApp integration for LIMBS Orthopaedic

/**
 * Open WhatsApp chat with pre-filled message
 * @param {string} phoneNumber - WhatsApp phone number in international format
 * @param {string} message - Pre-filled message
 */
function openWhatsAppChat(phoneNumber, message) {
    // Encode the message for URL
    const encodedMessage = encodeURIComponent(message);
    
    // Create WhatsApp URL
    const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodedMessage}`;
    
    // Open WhatsApp in new tab
    window.open(whatsappUrl, '_blank');
}

// Set up WhatsApp chat button event listeners
document.addEventListener('DOMContentLoaded', function() {
    const whatsappButtons = document.querySelectorAll('.whatsapp-btn');
    
    whatsappButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const phoneNumber = this.getAttribute('data-phone') || '254719628276';
            let message = this.getAttribute('data-message') || '';
            
            // If no custom message, use default
            if (!message) {
                const serviceTitle = this.getAttribute('data-service') || '';
                const serviceUrl = this.getAttribute('data-url') || '';
                
                if (serviceTitle) {
                    message = `Hello *LIMBS Orthopaedic*, I want ${serviceTitle} ${serviceUrl}`;
                } else {
                    message = 'Hello *LIMBS Orthopaedic*, I would like to inquire about your services.';
                }
            }
            
            openWhatsAppChat(phoneNumber, message);
        });
    });
});
