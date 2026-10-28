# 애니메이션 접촉 검수

공·물체가 바닥이나 그림자에 닿는 장면을 만들거나 고칠 때만 읽는다.

- For visible floor collisions, render the calculated impact frame and keep the ball's visible lower edge tangent to the shadow or floor after squash/stretch.
- Compensate `Position` for vertical compression so the squash does not lift the ball off the floor or push it through.
- Place the shadow behind the ball when possible; otherwise align its upper edge with no visible gap or overlap.
- 확인은 충돌 프레임 한 장으로 한다. 렌더 결과 파일 경로는 사용자가 지정한 곳에만 쓴다.
