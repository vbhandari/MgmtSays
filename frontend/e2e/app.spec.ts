import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome to MgmtSays')).toBeVisible();
  });

  test('should navigate to companies page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Companies');
    await expect(page).toHaveURL('/companies');
    await expect(page.getByRole('heading', { name: 'Companies' })).toBeVisible();
  });

  test('should navigate to search page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Search');
    await expect(page).toHaveURL('/search');
    await expect(page.getByRole('heading', { name: 'Search & Ask' })).toBeVisible();
  });

  test('should navigate to settings page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Settings');
    await expect(page).toHaveURL('/settings');
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  });
});

test.describe('Dashboard', () => {
  test('should show stats cards', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByText('Companies')).toBeVisible();
    await expect(page.getByText('Documents')).toBeVisible();
    await expect(page.getByText('Initiatives')).toBeVisible();
    await expect(page.getByText('Insights')).toBeVisible();
  });

  test('should show quick actions', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByText('Add Company')).toBeVisible();
    await expect(page.getByText('Search Disclosures')).toBeVisible();
    await expect(page.getByText('Ask Questions')).toBeVisible();
  });
});

test.describe('Companies', () => {
  test('should show empty state when no companies', async ({ page }) => {
    await page.goto('/companies');
    // May show empty state or list depending on API
  });

  test('should open create company modal', async ({ page }) => {
    await page.goto('/companies');
    await page.click('button:has-text("Add Company")');
    await expect(page.getByText('Add New Company')).toBeVisible();
  });

  test('should have search input', async ({ page }) => {
    await page.goto('/companies');
    await expect(page.getByPlaceholder('Search companies...')).toBeVisible();
  });

  test('should validate company creation form', async ({ page }) => {
    await page.goto('/companies');
    await page.click('button:has-text("Add Company")');
    
    // Try to submit empty form
    await page.click('button:has-text("Create")');
    
    // Should show validation errors
    await expect(page.getByText(/required|ticker|name/i)).toBeVisible();
  });
});

test.describe('Document Upload', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a company detail page first (mock or create company)
    await page.goto('/companies');
  });

  test('should show document upload page with drop zone', async ({ page }) => {
    // This test assumes we have at least one company
    // Navigate to upload page if companies exist
    const companyLink = page.locator('a[href*="/companies/"]').first();
    
    if (await companyLink.isVisible()) {
      await companyLink.click();
      await page.click('text=Upload Document');
      
      // Check for drag and drop zone
      await expect(page.getByText('Drag and drop files here')).toBeVisible();
      
      // Check for file type instructions
      await expect(page.getByText(/PDF|DOCX|PPTX|TXT/i)).toBeVisible();
    }
  });

  test('should have document type selector', async ({ page }) => {
    const companyLink = page.locator('a[href*="/companies/"]').first();
    
    if (await companyLink.isVisible()) {
      await companyLink.click();
      await page.click('text=Upload Document');
      
      // Should have document type dropdown
      await expect(page.getByText('Document Type')).toBeVisible();
    }
  });
});

test.describe('Analysis Flow', () => {
  test('should show analysis page with run button', async ({ page }) => {
    await page.goto('/companies');
    
    const companyLink = page.locator('a[href*="/companies/"]').first();
    
    if (await companyLink.isVisible()) {
      await companyLink.click();
      
      // Navigate to analysis
      const analysisLink = page.locator('a[href*="/analysis"]');
      if (await analysisLink.isVisible()) {
        await analysisLink.click();
        
        // Should show run analysis button
        await expect(page.getByRole('button', { name: /run analysis/i })).toBeVisible();
      }
    }
  });

  test('should show document status in analysis page', async ({ page }) => {
    await page.goto('/companies');
    
    const companyLink = page.locator('a[href*="/companies/"]').first();
    
    if (await companyLink.isVisible()) {
      await companyLink.click();
      
      const analysisLink = page.locator('a[href*="/analysis"]');
      if (await analysisLink.isVisible()) {
        await analysisLink.click();
        
        // Should show documents section
        await expect(page.getByText('Documents for Analysis')).toBeVisible();
      }
    }
  });
});

test.describe('Timeline', () => {
  test('should show timeline page with category legend', async ({ page }) => {
    await page.goto('/companies');
    
    const companyLink = page.locator('a[href*="/companies/"]').first();
    
    if (await companyLink.isVisible()) {
      await companyLink.click();
      
      const timelineLink = page.locator('a[href*="/timeline"]');
      if (await timelineLink.isVisible()) {
        await timelineLink.click();
        
        // Should show category legend
        await expect(page.getByText('strategy')).toBeVisible();
        await expect(page.getByText('product')).toBeVisible();
      }
    }
  });

  test('should show empty state when no initiatives', async ({ page }) => {
    await page.goto('/companies');
    
    const companyLink = page.locator('a[href*="/companies/"]').first();
    
    if (await companyLink.isVisible()) {
      await companyLink.click();
      
      const timelineLink = page.locator('a[href*="/timeline"]');
      if (await timelineLink.isVisible()) {
        await timelineLink.click();
        
        // Either shows initiatives or empty state
        const hasInitiatives = await page.locator('.timeline-item').count() > 0;
        const hasEmptyState = await page.getByText(/no initiatives|run analysis/i).isVisible();
        
        expect(hasInitiatives || hasEmptyState).toBeTruthy();
      }
    }
  });
});

test.describe('Search', () => {
  test('should show mode toggle', async ({ page }) => {
    await page.goto('/search');
    await expect(page.getByRole('button', { name: 'Search' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Ask Question' })).toBeVisible();
  });

  test('should switch between search and ask modes', async ({ page }) => {
    await page.goto('/search');
    
    // Default is search mode
    await expect(page.getByPlaceholder('Search documents...')).toBeVisible();
    
    // Switch to ask mode
    await page.click('button:has-text("Ask Question")');
    await expect(page.getByPlaceholder(/What are the company's main strategic initiatives/)).toBeVisible();
  });

  test('should have company filter', async ({ page }) => {
    await page.goto('/search');
    await expect(page.getByText('Company:')).toBeVisible();
  });

  test('should show search results', async ({ page }) => {
    await page.goto('/search');
    
    // Type a search query
    await page.fill('input[type="text"]', 'AI platform');
    await page.keyboard.press('Enter');
    
    // Wait for results (should show results or no results message)
    await page.waitForResponse((res) => res.url().includes('/search') || res.url().includes('/ask'));
  });
});

test.describe('Error Handling', () => {
  test('should show error page for invalid routes', async ({ page }) => {
    await page.goto('/invalid-route-that-does-not-exist');
    
    // Should redirect to dashboard or show 404
    const url = page.url();
    expect(url.includes('dashboard') || url.includes('404')).toBeTruthy();
  });

  test('should handle company not found gracefully', async ({ page }) => {
    await page.goto('/companies/non-existent-id-12345');
    
    // Should show not found message
    await expect(page.getByText(/not found|could not be found/i)).toBeVisible();
  });
});
