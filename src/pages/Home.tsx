import { Link } from 'react-router-dom'

const stats = [
  { label: 'Total Patients', value: '1,284', icon: '👥', color: 'bg-blue-50 border-blue-200 text-blue-700' },
  { label: 'Appointments Today', value: '48', icon: '📅', color: 'bg-green-50 border-green-200 text-green-700' },
  { label: 'Active Doctors', value: '32', icon: '👨‍⚕️', color: 'bg-purple-50 border-purple-200 text-purple-700' },
  { label: 'Pending Reports', value: '7', icon: '📋', color: 'bg-orange-50 border-orange-200 text-orange-700' },
]

const quickLinks = [
  { to: '/appointments', label: 'Schedule Appointment', icon: '📅', desc: 'Book or manage patient appointments' },
  { to: '/doctors', label: 'View Doctors', icon: '👨‍⚕️', desc: 'Browse our medical staff' },
  { to: '/patients', label: 'Patient Records', icon: '📁', desc: 'Access and manage patient data' },
]

export default function Home() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-500">Welcome to Med — your medical management system</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className={`border rounded-xl p-5 ${stat.color}`}>
            <div className="text-3xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm font-medium mt-1 opacity-80">{stat.label}</div>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Access</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {quickLinks.map(({ to, label, icon, desc }) => (
            <Link
              key={to}
              to={to}
              className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md hover:border-blue-300 transition-all group"
            >
              <div className="text-4xl mb-3">{icon}</div>
              <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{label}</div>
              <div className="text-sm text-gray-500 mt-1">{desc}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
