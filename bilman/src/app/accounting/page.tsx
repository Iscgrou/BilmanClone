'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Payment {
  id: number;
  representativeId: number;
  amount: number;
  date: string;
  note: string;
}

export default function AccountingPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    representativeId: '',
    amount: '',
    date: '',
    note: '',
  });
  const [formError, setFormError] = useState('');

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/accounting');
      setPayments(response.data);
      setError('');
    } catch (err) {
      setError('خطا در بارگذاری پرداخت‌ها');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    if (!form.representativeId || !form.amount || !form.date) {
      setFormError('لطفا تمام فیلدهای اجباری را پر کنید');
      return;
    }
    try {
      await axios.post('/api/accounting', {
        representativeId: Number(form.representativeId),
        amount: Number(form.amount),
        date: form.date,
        note: form.note,
      });
      setForm({ representativeId: '', amount: '', date: '', note: '' });
      fetchPayments();
    } catch (err) {
      setFormError('خطا در ثبت پرداخت');
    }
  };

  return (
    <main className="p-6 bg-white rounded shadow max-w-5xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">مدیریت حسابداری</h1>

      {loading ? (
        <p>در حال بارگذاری...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : (
        <table className="w-full border border-gray-300 mb-6">
          <thead>
            <tr className="bg-gray-100 text-black">
              <th className="border border-gray-300 p-2">شناسه</th>
              <th className="border border-gray-300 p-2">شناسه نماینده</th>
              <th className="border border-gray-300 p-2">مبلغ</th>
              <th className="border border-gray-300 p-2">تاریخ</th>
              <th className="border border-gray-300 p-2">یادداشت</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id} className="text-black">
                <td className="border border-gray-300 p-2 text-center">{payment.id}</td>
                <td className="border border-gray-300 p-2">{payment.representativeId}</td>
                <td className="border border-gray-300 p-2">{payment.amount.toLocaleString()}</td>
                <td className="border border-gray-300 p-2">{payment.date}</td>
                <td className="border border-gray-300 p-2">{payment.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <form onSubmit={handleSubmit} className="max-w-md mx-auto" dir="rtl">
        <h2 className="text-xl font-semibold mb-4 text-black">ثبت پرداخت جدید</h2>
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
          <label htmlFor="date" className="block mb-1 text-black">تاریخ</label>
          <input
            id="date"
            name="date"
            type="text"
            placeholder="مثال: 1402/02/10"
            value={form.date}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-6">
          <label htmlFor="note" className="block mb-1 text-black">یادداشت</label>
          <textarea
            id="note"
            name="note"
            value={form.note}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            rows={3}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 transition"
        >
          ثبت پرداخت
        </button>
      </form>
    </main>
  );
}
