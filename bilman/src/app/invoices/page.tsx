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

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    representativeId: '',
    amount: '',
    status: '',
    date: '',
  });
  const [formError, setFormError] = useState('');

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
      setError('خطا در بارگذاری فاکتورها');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    if (!form.representativeId || !form.amount || !form.status || !form.date) {
      setFormError('لطفا تمام فیلدها را پر کنید');
      return;
    }
    try {
      await axios.post('/api/invoices', {
        representativeId: Number(form.representativeId),
        amount: Number(form.amount),
        status: form.status,
        date: form.date,
      });
      setForm({ representativeId: '', amount: '', status: '', date: '' });
      fetchInvoices();
    } catch (err) {
      setFormError('خطا در افزودن فاکتور');
    }
  };

  return (
    <main className="p-6 bg-white rounded shadow max-w-5xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">مدیریت فاکتورها</h1>

      {loading ? (
        <p>در حال بارگذاری...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : (
        <table className="w-full border border-gray-300 mb-6">
          <thead>
            <tr className="bg-gray-100 text-black">
              <th className="border border-gray-300 p-2">شناسه</th>
              <th className="border border-gray-300 p-2">نماینده</th>
              <th className="border border-gray-300 p-2">مبلغ</th>
              <th className="border border-gray-300 p-2">وضعیت</th>
              <th className="border border-gray-300 p-2">تاریخ</th>
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
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <form onSubmit={handleSubmit} className="max-w-md mx-auto" dir="rtl">
        <h2 className="text-xl font-semibold mb-4 text-black">افزودن فاکتور جدید</h2>
        {formError && <p className="text-red-600 mb-4">{formError}</p>}
        <div className="mb-4">
          <label htmlFor="representativeId" className="block mb-1 text-black">شناسه نماینده</label>
          <input
            id="representativeId"
            name="representativeId"
            type="number"
            value={form.representativeId}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="amount" className="block mb-1 text-black">مبلغ</label>
          <input
            id="amount"
            name="amount"
            type="number"
            value={form.amount}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="status" className="block mb-1 text-black">وضعیت</label>
          <select
            id="status"
            name="status"
            value={form.status}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          >
            <option value="">انتخاب کنید</option>
            <option value="پرداخت شده">پرداخت شده</option>
            <option value="پرداخت نشده">پرداخت نشده</option>
          </select>
        </div>
        <div className="mb-6">
          <label htmlFor="date" className="block mb-1 text-black">تاریخ</label>
          <input
            id="date"
            name="date"
            type="text"
            placeholder="مثال: 1402/02/01"
            value={form.date}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 transition"
        >
          افزودن فاکتور
        </button>
      </form>
    </main>
  );
}
