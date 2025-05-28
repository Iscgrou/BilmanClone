'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Representative {
  id: number;
  name: string;
  phone: string;
  email: string;
}

export default function RepresentativesPage() {
  const [representatives, setRepresentatives] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ name: '', phone: '', email: '' });
  const [formError, setFormError] = useState('');

  useEffect(() => {
    fetchRepresentatives();
  }, []);

  const fetchRepresentatives = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/representatives');
      setRepresentatives(response.data);
      setError('');
    } catch (err) {
      setError('خطا در بارگذاری نمایندگان');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    if (!form.name || !form.phone || !form.email) {
      setFormError('لطفا تمام فیلدها را پر کنید');
      return;
    }
    try {
      await axios.post('/api/representatives', form);
      setForm({ name: '', phone: '', email: '' });
      fetchRepresentatives();
    } catch (err) {
      setFormError('خطا در افزودن نماینده');
    }
  };

  return (
    <main className="p-6 bg-white rounded shadow max-w-4xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">مدیریت نمایندگان</h1>

      {loading ? (
        <p>در حال بارگذاری...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : (
        <table className="w-full border border-gray-300 mb-6">
          <thead>
            <tr className="bg-gray-100 text-black">
              <th className="border border-gray-300 p-2">شناسه</th>
              <th className="border border-gray-300 p-2">نام</th>
              <th className="border border-gray-300 p-2">تلفن</th>
              <th className="border border-gray-300 p-2">ایمیل</th>
            </tr>
          </thead>
          <tbody>
            {representatives.map((rep) => (
              <tr key={rep.id} className="text-black">
                <td className="border border-gray-300 p-2 text-center">{rep.id}</td>
                <td className="border border-gray-300 p-2">{rep.name}</td>
                <td className="border border-gray-300 p-2">{rep.phone}</td>
                <td className="border border-gray-300 p-2">{rep.email}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <form onSubmit={handleSubmit} className="max-w-md mx-auto" dir="rtl">
        <h2 className="text-xl font-semibold mb-4 text-black">افزودن نماینده جدید</h2>
        {formError && <p className="text-red-600 mb-4">{formError}</p>}
        <div className="mb-4">
          <label htmlFor="name" className="block mb-1 text-black">نام</label>
          <input
            id="name"
            name="name"
            type="text"
            value={form.name}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="phone" className="block mb-1 text-black">تلفن</label>
          <input
            id="phone"
            name="phone"
            type="text"
            value={form.phone}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-6">
          <label htmlFor="email" className="block mb-1 text-black">ایمیل</label>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 transition"
        >
          افزودن نماینده
        </button>
      </form>
    </main>
  );
}
