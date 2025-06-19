/**
 * Admin notification handling JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get notification elements
    const notificationBadges = document.querySelectorAll('.notification-badge');
    const markReadButtons = document.querySelectorAll('.mark-notification-read');
    const markAllReadButton = document.querySelector('#mark-all-notifications-read');
    
    // Add click handlers to mark-read buttons
    if (markReadButtons.length > 0) {
        markReadButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const notificationId = this.dataset.notificationId;
                markNotificationAsRead(notificationId, this);
            });
        });
    }
    
    // Add click handler to mark-all-read button
    if (markAllReadButton) {
        markAllReadButton.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsAsRead();
        });
    }
    
    /**
     * Mark a single notification as read
     */
    function markNotificationAsRead(notificationId, buttonEl) {
        // Create form data
        const formData = new FormData();
        formData.append('notification_id', notificationId);
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send request
        fetch('/admin/notifications/mark-read/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the notification item or update UI
                const listItem = buttonEl.closest('li');
                if (listItem) {
                    listItem.classList.add('read');
                    listItem.style.opacity = '0.6';
                    buttonEl.textContent = 'Marked as Read';
                    buttonEl.disabled = true;
                }
                
                // Update badge counts
                updateNotificationBadges(data.unread_count);
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    }
    
    /**
     * Mark all notifications as read
     */
    function markAllNotificationsAsRead() {
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send request
        fetch('/admin/notifications/mark-all-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mark all items as read in UI
                const listItems = document.querySelectorAll('.notification-item:not(.read)');
                listItems.forEach(item => {
                    item.classList.add('read');
                    item.style.opacity = '0.6';
                    
                    const button = item.querySelector('.mark-notification-read');
                    if (button) {
                        button.textContent = 'Marked as Read';
                        button.disabled = true;
                    }
                });
                
                // Update badge counts
                updateNotificationBadges(0);
                
                // Show success message
                alert(`Marked ${data.marked_count} notifications as read.`);
            }
        })
        .catch(error => {
            console.error('Error marking all notifications as read:', error);
        });
    }
    
    /**
     * Update notification badge counts
     */
    function updateNotificationBadges(count) {
        notificationBadges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        });
    }
});