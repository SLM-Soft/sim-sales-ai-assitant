import React from 'react';
import { createRoot } from 'react-dom/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

type Theme = 'dark' | 'light' | 'neutral';

interface PdfOptions {
  fileName?: string;
  title?: string;
  theme?: Theme;
}

const PdfDocument: React.FC<{ markdown: string; title?: string }> = ({ markdown, title }) => (
  <div
    className="markdown-body pdf-export"
    style={{
      background: 'var(--color-surface)',
      color: 'var(--color-text)',
      padding: '24px 28px',
      borderRadius: '16px',
      border: '1px solid var(--color-border)',
      width: '100%',
      boxSizing: 'border-box',
      boxShadow: '0 10px 30px rgba(0,0,0,0.18)',
    }}
  >
    {title ? (
      <h2
        style={{
          marginTop: 0,
          marginBottom: '16px',
          fontSize: '20px',
          fontWeight: 700,
          letterSpacing: '-0.2px',
        }}
      >
        {title}
      </h2>
    ) : null}
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ ...props }) => (
          <a
            {...props}
            className="text-[var(--color-accent)] underline underline-offset-2 hover:opacity-80"
            target="_blank"
            rel="noreferrer"
          />
        ),
        table: ({ ...props }) => (
          <div className="overflow-x-auto">
            <table
              {...props}
              className="w-full border-collapse text-left"
              style={{ borderColor: 'var(--color-border)' }}
            />
          </div>
        ),
        th: ({ ...props }) => (
          <th {...props} className="border !px-3 !py-2" style={{ borderColor: 'var(--color-border)' }} />
        ),
        td: ({ ...props }) => (
          <td
            {...props}
            className="border !px-3 !py-2 align-top"
            style={{ borderColor: 'var(--color-border)' }}
          />
        ),
        p: ({ ...props }) => <p {...props} className="!mb-3 last:mb-0" />,
        ul: ({ ...props }) => <ul {...props} className="list-disc !pl-5 !mb-3" />,
        ol: ({ ...props }) => <ol {...props} className="list-decimal !pl-5 !mb-3" />,
        li: ({ ...props }) => <li {...props} className="!mb-1 last:mb-0" />,
      }}
    >
      {markdown}
    </ReactMarkdown>
  </div>
);

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const exportMarkdownToPdf = async (markdown: string, options: PdfOptions = {}) => {
  if (!markdown.trim() || typeof window === 'undefined') return;

  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.left = '-9999px';
  container.style.top = '0';
  container.style.width = '800px';
  container.style.padding = '12px';
  container.style.background = 'transparent';
  container.style.zIndex = '-1';
  container.style.fontFamily = getComputedStyle(document.body).fontFamily || 'inherit';

  const activeTheme =
    options.theme ||
    Array.from(document.documentElement.classList).find((cls) => cls.startsWith('theme-'))?.replace('theme-', '') ||
    'dark';

  container.classList.add(`theme-${activeTheme}`);
  document.body.appendChild(container);

  const root = createRoot(container);
  root.render(<PdfDocument markdown={markdown} title={options.title} />);

  // let the browser paint hidden content before capture
  await sleep(40);

  const canvas = await html2canvas(container, {
    scale: 2,
    backgroundColor:
      getComputedStyle(document.documentElement).getPropertyValue('--color-bg')?.trim() || '#ffffff',
    windowWidth: container.scrollWidth,
  });

  const imgData = canvas.toDataURL('image/png');

  const pdf = new jsPDF('p', 'pt', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();

  const margin = 24;
  const imgWidth = pageWidth - margin * 2;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = margin;

  pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + margin;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
  }

  pdf.save(options.fileName || 'answer.pdf');

  root.unmount();
  container.remove();
};

export const exportElementToPdf = async (element: HTMLElement, options: PdfOptions = {}) => {
  if (!element || typeof window === 'undefined') return;

  const rect = element.getBoundingClientRect();
  const activeTheme =
    options.theme ||
    Array.from(document.documentElement.classList).find((cls) => cls.startsWith('theme-'))?.replace('theme-', '') ||
    'dark';

  // Ensure theme class is on cloned wrapper
  const wrapper = document.createElement('div');
  wrapper.className = `theme-${activeTheme}`;
  wrapper.style.position = 'absolute';
  wrapper.style.left = '-9999px';
  wrapper.style.top = '0';
  wrapper.style.padding = '16px';
  wrapper.style.background = getComputedStyle(document.documentElement).getPropertyValue('--color-bg') || '#ffffff';
  wrapper.style.fontFamily = getComputedStyle(document.body).fontFamily || 'inherit';
  wrapper.style.width = `${rect.width}px`;

  const clone = element.cloneNode(true) as HTMLElement;
  clone.style.width = '100%';
  clone.querySelectorAll<HTMLElement>('[data-export-hide="true"]').forEach((el) => {
    el.style.display = 'none';
  });
  wrapper.appendChild(clone);
  document.body.appendChild(wrapper);

  // wait for layout
  await sleep(40);

  const canvas = await html2canvas(clone, {
    scale: 2,
    backgroundColor:
      getComputedStyle(document.documentElement).getPropertyValue('--color-bg')?.trim() || '#ffffff',
    windowWidth: clone.scrollWidth,
  });

  const imgData = canvas.toDataURL('image/png');
  const pdf = new jsPDF('p', 'pt', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();

  const margin = 24;
  const imgWidth = pageWidth - margin * 2;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = margin;

  pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + margin;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
  }

  pdf.save(options.fileName || 'chat.pdf');
  wrapper.remove();
};
