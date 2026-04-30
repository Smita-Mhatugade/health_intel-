import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import type { HistoryEntry } from "@/store/useStore";

export function exportHistoryToPDF(entries: HistoryEntry[], userName?: string) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();

  // Header
  doc.setFillColor(15, 118, 110); // teal-700
  doc.rect(0, 0, pageWidth, 70, "F");
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(20);
  doc.setFont("helvetica", "bold");
  doc.text("HealthIntel — Analysis Report", 40, 35);
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text(
    `${userName ? "Patient: " + userName + "  •  " : ""}Generated: ${new Date().toLocaleString()}`,
    40,
    55
  );

  doc.setTextColor(30, 41, 59);
  let y = 100;

  if (entries.length === 0) {
    doc.setFontSize(12);
    doc.text("No analyses recorded.", 40, y);
  } else {
    const sorted = [...entries].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    const range = `${new Date(sorted[sorted.length - 1].timestamp).toLocaleDateString()} — ${new Date(
      sorted[0].timestamp
    ).toLocaleDateString()}`;
    doc.setFontSize(11);
    doc.text(`Date range: ${range}`, 40, y);
    doc.text(`Total entries: ${entries.length}`, 40, y + 16);
    y += 36;

    autoTable(doc, {
      startY: y,
      head: [["Date", "Category", "Prediction", "Confidence", "Severity"]],
      body: sorted.map((e) => [
        new Date(e.timestamp).toLocaleString(),
        e.diseaseCategory,
        e.prediction_label,
        `${e.confidence}%`,
        e.severity?.label ?? "—",
      ]),
      headStyles: { fillColor: [15, 118, 110], textColor: 255 },
      styles: { fontSize: 9, cellPadding: 6 },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      margin: { left: 40, right: 40 },
    });

    y = (doc as any).lastAutoTable.finalY + 24;

    sorted.forEach((e, i) => {
      if (y > 720) {
        doc.addPage();
        y = 60;
      }
      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.setTextColor(15, 118, 110);
      doc.text(`${i + 1}. ${e.diseaseCategory} — ${e.prediction_label}`, 40, y);
      y += 16;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9);
      doc.setTextColor(100, 116, 139);
      doc.text(`${new Date(e.timestamp).toLocaleString()}  •  Confidence: ${e.confidence}%  •  ${e.severity?.label ?? ""}`, 40, y);
      y += 14;
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(10);
      const lines = doc.splitTextToSize(e.summary || "—", pageWidth - 80);
      doc.text(lines, 40, y);
      y += lines.length * 12 + 16;
    });
  }

  // Footer disclaimer
  const pageCount = (doc as any).internal.getNumberOfPages();
  for (let p = 1; p <= pageCount; p++) {
    doc.setPage(p);
    doc.setFontSize(8);
    doc.setTextColor(148, 163, 184);
    doc.text(
      "For informational purposes only. Not a substitute for professional medical advice.",
      40,
      doc.internal.pageSize.getHeight() - 24
    );
    doc.text(`Page ${p} / ${pageCount}`, pageWidth - 80, doc.internal.pageSize.getHeight() - 24);
  }

  doc.save(`healthintel-report-${Date.now()}.pdf`);
}
