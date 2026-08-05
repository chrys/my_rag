document.addEventListener('DOMContentLoaded', function () {
    function initCustomPromptToggle() {
        const checkbox = document.querySelector('input[name="custom_prompt"]');
        const textarea = document.querySelector('textarea[name="custom_prompt_text"]');
        if (!checkbox || !textarea) return;

        // Locate the form field container row for custom_prompt_text
        let row = textarea.closest('.form-row, .field-custom_prompt_text') || textarea.parentElement;
        
        // Find outer wrapper in case of custom admin themes (like Unfold)
        while (row && row.parentElement && !row.classList.contains('form-row') && !row.classList.contains('field-custom_prompt_text') && row.parentElement.tagName !== 'FIELDSET' && row.parentElement.tagName !== 'FORM') {
            if (row.parentElement.classList.contains('form-row') || row.parentElement.classList.contains('field-custom_prompt_text') || row.parentElement.querySelector('label[for="id_custom_prompt_text"]')) {
                row = row.parentElement;
                break;
            }
            row = row.parentElement;
        }

        function updateVisibility() {
            if (checkbox.checked) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }

        checkbox.removeEventListener('change', updateVisibility);
        checkbox.addEventListener('change', updateVisibility);
        updateVisibility();
    }

    function initDisableThinkingToggle() {
        const select = document.querySelector('select[name="llm_model"]');
        const disableThinkingInput = document.querySelector('input[name="disable_thinking"]');
        if (!select || !disableThinkingInput) return;

        let row = disableThinkingInput.closest('.form-row, .field-disable_thinking') || disableThinkingInput.parentElement;
        while (row && row.parentElement && !row.classList.contains('form-row') && !row.classList.contains('field-disable_thinking') && row.parentElement.tagName !== 'FIELDSET' && row.parentElement.tagName !== 'FORM') {
            if (row.parentElement.classList.contains('form-row') || row.parentElement.classList.contains('field-disable_thinking') || row.parentElement.querySelector('label[for="id_disable_thinking"]')) {
                row = row.parentElement;
                break;
            }
            row = row.parentElement;
        }

        function updateThinkingVisibility() {
            const val = (select.value || '').toLowerCase();
            if (val.includes('gemma')) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }

        select.removeEventListener('change', updateThinkingVisibility);
        select.addEventListener('change', updateThinkingVisibility);
        updateThinkingVisibility();
    }

    initCustomPromptToggle();
    initDisableThinkingToggle();
    setTimeout(function() {
        initCustomPromptToggle();
        initDisableThinkingToggle();
    }, 300);
    setTimeout(function() {
        initCustomPromptToggle();
        initDisableThinkingToggle();
    }, 1000);
});
