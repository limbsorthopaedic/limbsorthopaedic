// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSearchFunctionality();
    initThemeToggle();
    initMobileMenu();
    initScrollToTop();
    initAnimations();
});

// Search functionality
function initSearchFunctionality() {
    const searchInput = document.getElementById('search-input');
    const mobileSearchInput = document.getElementById('mobile-search-input');
    const searchSuggestions = document.getElementById('search-suggestions');
    const mobileSearchSuggestions = document.getElementById('mobile-search-suggestions');

    if (searchInput && searchSuggestions) {
        setupSearchInput(searchInput, searchSuggestions);
    }

    if (mobileSearchInput && mobileSearchSuggestions) {
        setupSearchInput(mobileSearchInput, mobileSearchSuggestions);
    }
}

function setupSearchInput(input, suggestionsContainer) {
    let debounceTimer;
    let currentRequest = null;

    input.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(debounceTimer);
        
        // Cancel previous request if it exists
        if (currentRequest) {
            currentRequest.abort();
            currentRequest = null;
        }
        
        if (query.length < 2) {
            suggestionsContainer.classList.add('hidden');
            return;
        }

        debounceTimer = setTimeout(() => {
            currentRequest = fetchSearchSuggestions(query, suggestionsContainer);
        }, 200); // Faster response for better UX
    });

    input.addEventListener('focus', function() {
        const query = this.value.trim();
        if (query.length >= 2) {
            currentRequest = fetchSearchSuggestions(query, suggestionsContainer);
        }
    });

    // Enhanced keyboard navigation
    input.addEventListener('keydown', function(e) {
        const suggestions = suggestionsContainer.querySelectorAll('a');
        const activeSuggestion = suggestionsContainer.querySelector('.suggestion-active');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (activeSuggestion) {
                activeSuggestion.classList.remove('suggestion-active');
                const next = activeSuggestion.nextElementSibling;
                if (next) {
                    next.classList.add('suggestion-active');
                } else {
                    suggestions[0]?.classList.add('suggestion-active');
                }
            } else {
                suggestions[0]?.classList.add('suggestion-active');
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (activeSuggestion) {
                activeSuggestion.classList.remove('suggestion-active');
                const prev = activeSuggestion.previousElementSibling;
                if (prev) {
                    prev.classList.add('suggestion-active');
                } else {
                    suggestions[suggestions.length - 1]?.classList.add('suggestion-active');
                }
            } else {
                suggestions[suggestions.length - 1]?.classList.add('suggestion-active');
            }
        } else if (e.key === 'Enter') {
            if (activeSuggestion) {
                e.preventDefault();
                activeSuggestion.click();
            }
        } else if (e.key === 'Escape') {
            suggestionsContainer.classList.add('hidden');
            input.blur();
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.classList.add('hidden');
        }
    });
}

function fetchSearchSuggestions(query, container) {
    const controller = new AbortController();
    
    const request = fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`, {
        signal: controller.signal
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displaySearchSuggestions(data.suggestions || [], container);
        })
        .catch(error => {
            if (error.name !== 'AbortError') {
                console.log('Search suggestions error:', error);
                container.classList.add('hidden');
            }
        });
    
    // Return controller so we can abort the request if needed
    request.abort = () => controller.abort();
    return request;
}

function displaySearchSuggestions(suggestions, container) {
    if (suggestions.length === 0) {
        container.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500 text-center">No results found</div>';
        container.classList.remove('hidden');
        return;
    }

    // Group suggestions by category
    const groupedSuggestions = suggestions.reduce((acc, suggestion) => {
        const category = suggestion.category || 'Other';
        if (!acc[category]) {
            acc[category] = [];
        }
        acc[category].push(suggestion);
        return acc;
    }, {});

    let html = '';
    
    // Add "View all results" option at the top
    if (suggestions.length > 0) {
        const query = container.closest('.relative').querySelector('input').value;
        html += `<a href="/search/?q=${encodeURIComponent(query)}" class="block px-4 py-2 hover:bg-blue-50 border-b border-gray-100 transition-colors bg-blue-50">
            <div class="flex items-center">
                <i class="fas fa-search text-blue-600 mr-3 text-sm"></i>
                <div class="flex-1">
                    <div class="font-medium text-sm text-blue-900">View all results for "${query}"</div>
                </div>
            </div>
        </a>`;
    }

    // Display suggestions grouped by category
    Object.entries(groupedSuggestions).forEach(([category, items]) => {
        if (items.length > 0) {
            // Category header
            html += `<div class="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide bg-gray-50 border-b border-gray-100">${category}</div>`;
            
            // Items in category
            items.forEach((suggestion, index) => {
                const truncatedDescription = suggestion.description && suggestion.description.length > 80 
                    ? suggestion.description.substring(0, 80) + '...' 
                    : suggestion.description;

                html += `<a href="${suggestion.url}" class="block px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors suggestion-item" data-category="${category}">
                    <div class="flex items-start">
                        <i class="${suggestion.icon || 'fas fa-search'} text-primary mr-3 text-sm mt-0.5 flex-shrink-0"></i>
                        <div class="flex-1 min-w-0">
                            <div class="font-medium text-sm text-gray-900 truncate">${suggestion.title}</div>
                            ${truncatedDescription ? `<div class="text-xs text-gray-600 mt-1 line-clamp-2">${truncatedDescription}</div>` : ''}
                        </div>
                        <div class="flex-shrink-0 ml-2">
                            <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
                        </div>
                    </div>
                </a>`;
            });
        }
    });

    container.innerHTML = html;
    container.classList.remove('hidden');

    // Add hover effects and keyboard navigation support
    const suggestionItems = container.querySelectorAll('.suggestion-item');
    suggestionItems.forEach((item, index) => {
        item.addEventListener('mouseenter', function() {
            // Remove active class from all items
            suggestionItems.forEach(si => si.classList.remove('suggestion-active'));
            // Add active class to hovered item
            this.classList.add('suggestion-active');
        });

        item.addEventListener('mouseleave', function() {
            this.classList.remove('suggestion-active');
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initSearchFunctionality();
});

function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // Theme toggle functionality
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

function initMobileMenu() {
    const mobileMenuButton = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const isHidden = mobileMenu.classList.contains('hidden');
            
            if (isHidden) {
                mobileMenu.classList.remove('hidden');
                mobileMenu.style.display = 'block';
            } else {
                mobileMenu.classList.add('hidden');
                mobileMenu.style.display = 'none';
            }
            
            // Update aria-expanded attribute for accessibility
            mobileMenuButton.setAttribute('aria-expanded', !isHidden);
        });
    }

    // Initialize user dropdown functionality
    initUserDropdown();
}

function initUserDropdown() {
    const userDropdown = document.querySelector('.user-dropdown');
    if (!userDropdown) return;

    const toggleButton = userDropdown.querySelector('.user-dropdown-toggle');
    const dropdownMenu = userDropdown.querySelector('.user-dropdown-menu');

    if (toggleButton && dropdownMenu) {
        // Initially hide the dropdown
        dropdownMenu.style.display = 'none';
        dropdownMenu.style.position = 'absolute';
        dropdownMenu.style.right = '0';
        dropdownMenu.style.top = '100%';
        dropdownMenu.style.marginTop = '0.25rem';
        dropdownMenu.style.zIndex = '50';

        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isVisible = dropdownMenu.style.display === 'block';
            const chevronIcon = toggleButton.querySelector('i');
            
            if (isVisible) {
                dropdownMenu.style.display = 'none';
                if (chevronIcon) {
                    chevronIcon.classList.remove('fa-chevron-up');
                    chevronIcon.classList.add('fa-chevron-down');
                }
            } else {
                dropdownMenu.style.display = 'block';
                if (chevronIcon) {
                    chevronIcon.classList.remove('fa-chevron-down');
                    chevronIcon.classList.add('fa-chevron-up');
                }
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target)) {
                dropdownMenu.style.display = 'none';
                const chevronIcon = toggleButton.querySelector('i');
                if (chevronIcon) {
                    chevronIcon.classList.remove('fa-chevron-up');
                    chevronIcon.classList.add('fa-chevron-down');
                }
            }
        });

        // Close dropdown when pressing Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                dropdownMenu.style.display = 'none';
                const chevronIcon = toggleButton.querySelector('i');
                if (chevronIcon) {
                    chevronIcon.classList.remove('fa-chevron-up');
                    chevronIcon.classList.add('fa-chevron-down');
                }
            }
        });
    }
}

function initScrollToTop() {
    const scrollToTopButton = document.getElementById('scroll-to-top');

    if (scrollToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopButton.classList.remove('hidden');
            } else {
                scrollToTopButton.classList.add('hidden');
            }
        });

        scrollToTopButton.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

function initAnimations() {
    // Add scroll animations and other UI enhancements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}