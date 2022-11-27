import React, { lazy, Suspense } from 'react';

const LazyBottomBar = lazy(() => import('./BottomBar'));

const BottomBar = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyBottomBar {...props} />
  </Suspense>
);

export default BottomBar;
