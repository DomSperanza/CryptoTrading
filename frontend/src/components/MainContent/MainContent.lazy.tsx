import React, { lazy, Suspense } from 'react';

const LazyMainContent = lazy(() => import('./MainContent'));

const MainContent = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyMainContent {...props} />
  </Suspense>
);

export default MainContent;
