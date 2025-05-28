'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Invoice {
  id: number;
  representativeId: number;
  amount: number;
  status: string;
  date: string;
}

export default function InvoiceStatusPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/invoices');
      setInvoices(response.data);
      setError('');
    } catch (err) {
      setError('خطا در بارگذاری وضعیت فاکتورها');
    } finally {
      setLoading(false);
    }
  };

  const toggleStatus = async (invoice: Invoice) => {
    const newStatus = invoice.status === 'پرداخت شده' ? 'پرداخت نشده' : 'پرداخت شده';
    try {
      // Here you would call an API to update the invoice status
      // For now, we update locally
      setInvoices((prev) =>
        prev.map((inv) =>
          inv.id === invoice.id ? { ...inv, status: newStatus } : inv
        )
      );
    } catch (err) {
      alert('خطا در تغییر وضعیت فاکتور');
    }
  };

  return (
    <main className="p-6 bg-white rounded shadow max-w-5xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">وضعیت فاکتورها</h1>

      {loading ? (
        <p>در حال بارگذاری...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : (
        <table className="w-full border border-gray-300">
          <thead>
            <tr className="bg-gray-100 text-black">
              <th className="border border-gray-300 p-2">شناسه</th>
              <th className="border border-gray-300 p-2">نماینده</th>
              <th className="border border-gray-300 p-2">مبلغ</th>
              <th className="border border-gray-300 p-2">وضعیت</th>
              <th className="border border-gray-300 p-2">تاریخ</th>
              <th className="border border-gray-300 p-2">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id} className="text-black">
                <td className="border border-gray-300 p-2 text-center">{inv.id}</td>
                <td className="border border-gray-300 p-2">{inv.representativeId}</td>
                <td className="border border-gray-300 p-2">{inv.amount.toLocaleString()}</td>
                <td className="border border-gray-300 p-2">{inv.status}</td>
                <td className="border border-gray-300 p-2">{inv.date}</td>
                <td className="border border-gray-300 p-2">
                  <button
                    onClick={() => toggleStatus(inv)}
                    className="bg-black text-white px-3 py-1 rounded hover:bg-gray-800 transition"
                  >
                    تغییر وضعیت
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
