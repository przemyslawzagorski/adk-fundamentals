import React, { useState, useEffect } from 'react';

interface Course {
  id: number;
  title: string;
  description: string;
  category: string;
  durationMinutes: number;
}

interface MigrationStatus {
  totalCourses: number;
  migratedCourses: number;
  failedCourses: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  // TODO: Add more detailed error messages or logs for failed courses
}

/**
 * React component for displaying and managing course migrations.
 * Demonstrates interaction with backend services for large data operations and AI integrations.
 */
const MigrationDashboard: React.FC = () => {
  const [rawCourseData, setRawCourseData] = useState<string>('');
  const [migrationStatus, setMigrationStatus] = useState<MigrationStatus | null>(null);
  const [migratedCourses, setMigratedCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // TODO: Use Copilot to implement a WebSocket connection for real-time migration status updates.
  // This would provide a better user experience for long-running migrations.
  // useEffect(() => {
  //   const ws = new WebSocket('ws://localhost:8080/ws/migration-status');
  //   ws.onmessage = (event) => {
  //     const statusUpdate: MigrationStatus = JSON.parse(event.data);
  //     setMigrationStatus(statusUpdate);
  //   };
  //   return () => ws.close();
  // }, []);

  const handleMigrationSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setMigrationStatus(null);
    setMigratedCourses([]);

    try {
      // Split raw data by newline, filter empty lines
      const dataArray = rawCourseData.split('\n').filter(line => line.trim() !== '');
      if (dataArray.length === 0) {
        setError('Please enter some raw course data to migrate.');
        setIsLoading(false);
        return;
      }

      // TODO: Use Copilot to validate the format of each raw data string before sending.
      // Provide user-friendly feedback for invalid entries.

      const response = await fetch('/api/v1/migrations/courses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataArray),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to start migration');
      }

      const result: Course[] = await response.json();
      setMigratedCourses(result);
      setMigrationStatus({
        totalCourses: dataArray.length,
        migratedCourses: result.length,
        failedCourses: dataArray.length - result.length,
        status: 'COMPLETED',
      });

      // TODO: Implement a mechanism to poll for migration status if WebSockets are not used.

    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred during migration.');
      setMigrationStatus({
        totalCourses: 0,
        migratedCourses: 0,
        failedCourses: 0,
        status: 'FAILED',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="migration-dashboard">
      <h1>Course Migration Dashboard</h1>

      <div className="input-section">
        <h2>Enter Raw Course Data</h2>
        <textarea
          rows={10}
          cols={60}
          value={rawCourseData}
          onChange={(e) => setRawCourseData(e.target.value)}
          placeholder="Enter one course per line. Example: \"Title;Duration;Category\""
          disabled={isLoading}
        ></textarea>
        <br />
        <button onClick={handleMigrationSubmit} disabled={isLoading}>
          {isLoading ? 'Migrating...' : 'Start Migration'}
        </button>
      </div>

      {error && (
        <div className="error-message" style={{ color: 'red' }}>
          <h3>Error:</h3>
          <p>{error}</p>
          {/* TODO: Use Copilot to suggest a retry mechanism for specific errors (e.g., AI rate limit). */}
        </div>
      )}

      {migrationStatus && (
        <div className="status-section">
          <h2>Migration Status</h2>
          <p>Status: <strong>{migrationStatus.status}</strong></p>
          <p>Total Courses Submitted: {migrationStatus.totalCourses}</p>
          <p>Successfully Migrated: {migrationStatus.migratedCourses}</p>
          <p>Failed Migrations: {migrationStatus.failedCourses}</p>
        </div>
      )}

      {migratedCourses.length > 0 && (
        <div className="migrated-courses">
          <h2>Migrated Courses</h2>
          <ul>
            {migratedCourses.map((course) => (
              <li key={course.id}>
                <strong>{course.title}</strong> ({course.category}) - {course.durationMinutes} min
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MigrationDashboard;
